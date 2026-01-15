from typing import List, AsyncGenerator, Any, TypedDict, Annotated, Literal
import json
import re
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage, ToolMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from .base_agent import BaseAgent
from ..schemas.stream import PlanEvent, StatusEvent, MessageEvent
from ..core.config import settings

# Import tools
from ..tools.healthcare.patient import patient_record
from ..tools.healthcare.coverage import coverage_check
from ..tools.healthcare.scheduling import appointment_slots
from ..tools.healthcare.meds import medication_info
from ..tools.healthcare.policy import policy_check

# Define state
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    next: str  # supervisor routing token

class HealthcareAgent(BaseAgent):
    """
    Healthcare Care Coordinator Agent using a supervisor-worker pattern.
    """
    
    def __init__(self):
        super().__init__("healthcare")
        self.tools = [patient_record, coverage_check, appointment_slots, medication_info, policy_check]
        self.tool_node = ToolNode(self.tools)
        
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL_NAME,
            temperature=0,
            openai_api_key=settings.OPENAI_API_KEY,
            openai_api_base=settings.OPENAI_API_BASE,
        )
        
        self.graph = self._build_graph()

    def _build_graph(self):
        builder = StateGraph(AgentState)
        
        builder.add_node("supervisor", self._supervisor_node)
        builder.add_node("triage_nurse", self._triage_nurse_node)
        builder.add_node("care_coordinator", self._care_coordinator_node)
        builder.add_node("tools", self.tool_node)
        
        builder.set_entry_point("supervisor")
        
        # Routing from supervisor
        builder.add_conditional_edges(
            "supervisor",
            lambda x: x["next"],
            {
                "triage_nurse": "triage_nurse",
                "care_coordinator": "care_coordinator",
                "end": END
            }
        )
        
        # After triage, if tool calls are present, go to tools
        builder.add_conditional_edges(
            "triage_nurse",
            self._should_continue,
            {
                "continue": "tools",
                "end": "supervisor"
            }
        )
        
        # After tools, always return to supervisor
        builder.add_edge("tools", "supervisor")
        
        # After coordinator, end
        builder.add_edge("care_coordinator", END)
        
        return builder.compile()

    def _extract_patient_id(self, text: str) -> str | None:
        match = re.search(r"\bPT-\d+\b", text, re.IGNORECASE)
        return match.group(0).upper() if match else None

    def _latest_user_text(self, messages: List[BaseMessage]) -> str:
        for msg in reversed(messages):
            if isinstance(msg, HumanMessage) and msg.content:
                return str(msg.content)
        return ""

    def _extract_date_range(self, messages: List[BaseMessage]) -> str | None:
        for msg in reversed(messages):
            if not isinstance(msg, HumanMessage) or not msg.content:
                continue
            text = str(msg.content).lower()
            match = re.search(r"\bnext\s+(two|2)\s+weeks\b", text)
            if match:
                return "next two weeks"
            match = re.search(r"\bnext\s+14\s+days\b", text)
            if match:
                return "next 14 days"
            match = re.search(r"\bwithin\s+the\s+next\s+(two|2)\s+weeks\b", text)
            if match:
                return "next two weeks"
        return None

    def _infer_intents(self, text: str) -> dict:
        lower = text.lower()
        return {
            "needs_patient": bool(re.search(r"\bpt-\d+\b", lower)) or "patient" in lower,
            "needs_policy": any(k in lower for k in ["policy", "mri", "ct", "scan", "imaging", "x-ray", "pet"]),
            "needs_coverage": any(k in lower for k in ["coverage", "copay", "insurance", "plan"]),
            "needs_slots": any(k in lower for k in ["appointment", "schedule", "slot", "availability", "visit", "booking"]),
            "needs_meds": any(k in lower for k in ["medication", "meds", "drug", "refill", "prescription", "albuterol", "amoxicillin", "oxycodone", "ibuprofen", "cetirizine"]),
        }

    def _collect_tool_results(self, messages: List[BaseMessage]) -> list[tuple[str | None, str]]:
        results: list[tuple[str | None, str]] = []
        for msg in messages:
            if isinstance(msg, ToolMessage) or getattr(msg, "type", None) == "tool":
                name = getattr(msg, "name", None) or getattr(msg, "tool", None)
                if not name and hasattr(msg, "additional_kwargs"):
                    name = msg.additional_kwargs.get("name") or msg.additional_kwargs.get("tool")
                content = getattr(msg, "content", "") or ""
                results.append((name, content))
        return results

    def _collect_tool_calls(self, messages: List[BaseMessage]) -> list[dict]:
        calls: list[dict] = []
        for msg in messages:
            tool_calls = getattr(msg, "tool_calls", None)
            if tool_calls:
                for call in tool_calls:
                    if isinstance(call, dict):
                        calls.append(call)
                    elif hasattr(call, "dict"):
                        calls.append(call.dict())
        return calls

    def _has_patient_result(self, messages: List[BaseMessage]) -> bool:
        for name, content in self._collect_tool_results(messages):
            if name != "patient_record":
                continue
            try:
                payload = json.loads(content)
                if isinstance(payload, dict) and (payload.get("patient_id") or payload.get("name")):
                    return True
            except Exception:
                if "not found" not in content.lower() and "error" not in content.lower():
                    return True
        return False

    def _has_policy_result(self, messages: List[BaseMessage]) -> bool:
        for name, content in self._collect_tool_results(messages):
            if name != "policy_check":
                continue
            try:
                payload = json.loads(content)
                if isinstance(payload, dict) and payload.get("status"):
                    return True
            except Exception:
                if "requires_review" in content.lower() or "blocked" in content.lower() or "pass" in content.lower():
                    return True
        return False

    def _build_plan_steps(self, user_text: str) -> list[dict]:
        intents = self._infer_intents(user_text)
        actions: list[str] = []
        if intents["needs_patient"]:
            actions.append("patient information")
        if intents["needs_policy"]:
            actions.append("policy requirements")
        if intents["needs_coverage"]:
            actions.append("coverage details")
        if intents["needs_slots"]:
            actions.append("appointment availability")
        if intents["needs_meds"]:
            actions.append("medication info")

        if actions:
            triage_desc = f"Triage: gather {', '.join(actions)}"
        else:
            triage_desc = "Triage: assess request and gather required details"

        return [
            {"id": "triage", "description": triage_desc, "status": "pending"},
            {"id": "coordination", "description": "Synthesize care coordination plan", "status": "pending"},
        ]

    def _should_stream_node(self, node: str | None) -> bool:
        if not node:
            return False
        if settings.HEALTHCARE_STREAM_NODES:
            return node in settings.HEALTHCARE_STREAM_NODES
        return True

    async def _should_continue(self, state: AgentState):
        messages = state["messages"]
        # If any tool calls are pending, continue to tools node for execution.
        tool_calls = self._collect_tool_calls(messages)
        if tool_calls:
            return "continue"
        return "end"

    async def _supervisor_node(self, state: AgentState):
        msgs = state["messages"]
        # Count tool outputs to prevent infinite loops (robust to ToolMessage vs tool_calls attr)
        tool_call_count = len(self._collect_tool_results(msgs))
        pending_tool_calls = len(self._collect_tool_calls(msgs))
        
        # Check for key data points based on tool outputs
        has_patient = self._has_patient_result(msgs)
        has_policy = self._has_policy_result(msgs)
        
        print(f"\n--- SUPERVISOR NODE ({len(msgs)} msgs, {tool_call_count} tool calls) ---")
        print(f"Status: patient={has_patient}, policy={has_policy}")
        
        # If there are pending tool calls, always return to triage/tools
        if pending_tool_calls:
            print("Decision: triage_nurse (pending tool calls)")
            return {"next": "triage_nurse"}

        # If we have the basics or have tried too many times, go to coordinator
        if (has_patient and has_policy) or tool_call_count >= 6:
            print("Decision: care_coordinator")
            return {"next": "care_coordinator"}

        # If triage didn't trigger any tool calls, avoid looping forever
        if tool_call_count == 0 and len(msgs) >= 2:
            print("Decision: care_coordinator (no tool calls)")
            return {"next": "care_coordinator"}
        
        print("Decision: triage_nurse")
        return {"next": "triage_nurse"}

    async def _triage_nurse_node(self, state: AgentState):
        print("--- TRIAGE NURSE NODE ---")
        user_text = self._latest_user_text(state["messages"])
        patient_id = self._extract_patient_id(user_text)
        date_range = self._extract_date_range(state["messages"])
        sys = SystemMessage(content=(
            "You are a triage nurse. Use tools to gather facts relevant to the user's request.\n"
            f"User request: {user_text or '(no user text provided)'}\n"
            f"Detected patient_id: {patient_id or '(none)'}\n"
            f"Known date_range: {date_range or '(none)'}\n"
            "Guidance:\n"
            "- If a patient_id is available, call patient_record(patient_id=...).\n"
            "- If the request mentions imaging (MRI/CT/scan), call policy_check(request_type='imaging', details='<request>').\n"
            "- If the request mentions medication, call medication_info(drug=...).\n"
            "- If coverage/cost is asked and you have plan/service, call coverage_check(insurance_plan=..., service=...).\n"
            "- If scheduling is requested and you have clinic/specialty/date_range, call appointment_slots(...).\n"
            "If required details are missing, ask a brief clarification question.\n"
            "If a Known date_range is provided, do not ask for date range or default to a different window; reuse the wording given."
        ))
        ai_msg = await self.llm.bind_tools(self.tools).ainvoke([sys] + state["messages"])
        return {"messages": [ai_msg]}

    async def _care_coordinator_node(self, state: AgentState):
        print("--- CARE COORDINATOR NODE ---")
        sys = SystemMessage(content=(
            "You are a care coordinator. Review the gathered facts from tool outputs.\n"
            "Write a clear 3-paragraph plan: Summary, Appointment Details, and Coverage/Instructions.\n"
            "Reference the patient by name if available, and cite any policy requirements that apply."
        ))
        response = await self.llm.ainvoke([sys] + state["messages"])
        return {"messages": [response]}

    async def process(self, message: str, history: List[BaseMessage]) -> dict:
        messages = history + [HumanMessage(content=message)]
        result = await self.graph.ainvoke({"messages": messages}, config={"recursion_limit": settings.HEALTHCARE_RECURSION_LIMIT})
        return {"content": result["messages"][-1].content}

    async def astream_events(self, message: str, history: List[BaseMessage]) -> AsyncGenerator[Any, None]:
        # Initial Plan
        yield PlanEvent(steps=self._build_plan_steps(message))

        messages = history + [HumanMessage(content=message)]
        
        # We manually stream node-by-node for better status updates
        state = {"messages": messages, "next": ""}
        triage_completed_sent = False
        
        # 1. Triage Phase
        yield StatusEvent(step_id="triage", status="running", details="Starting triage process...")
        
        async for event in self.graph.astream_events(state, version="v1", config={"recursion_limit": settings.HEALTHCARE_RECURSION_LIMIT}):
            kind = event["event"]
            
            # Catch token streams
            if kind == "on_chat_model_stream":
                metadata = event.get("metadata", {})
                node = metadata.get("langgraph_node")
                
                # DEBUG: Print metadata to trace node names in the graph
                # print(f"DEBUG: Node: {node}, Meta: {metadata}")
                
                if self._should_stream_node(node):
                    content = event["data"]["chunk"].content
                    if content:
                        yield MessageEvent(content=content, is_final=False)
            
            elif kind == "on_tool_start":
                tool_name = event["name"]
                yield StatusEvent(step_id="triage", status="running", details=f"Calling tool: {tool_name}...")
            
            elif kind == "on_node_start":
                node = event["name"]
                if node == "care_coordinator":
                    # Mark triage as done once we reach coordination
                    yield StatusEvent(step_id="triage", status="completed", details="Triage complete.")
                    yield StatusEvent(step_id="coordination", status="running", details="Drafting care plan...")
                    triage_completed_sent = True
            
            elif kind == "on_node_end":
                node = event["name"]
                if node == "triage_nurse":
                    # Update status after triage node finishes
                    yield StatusEvent(step_id="triage", status="running", details="Triage logic complete, checking supervisor...")
        
        if not triage_completed_sent:
            yield StatusEvent(step_id="triage", status="completed", details="Triage complete.")
        yield StatusEvent(step_id="coordination", status="completed", details="Care plan complete.")
        yield MessageEvent(content="", is_final=True)

    def get_agent_info(self) -> dict:
        return {
            "id": "healthcare",
            "name": "Healthcare Coordinator",
            "description": "Orchestrates triage, policy checks, and care planning.",
            "type": "orchestrator"
        }
