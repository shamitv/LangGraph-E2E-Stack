from typing import List, AsyncGenerator, Any, TypedDict, Annotated, Literal
import json
import re
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage
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

    async def _should_continue(self, state: AgentState):
        messages = state["messages"]
        last_message = messages[-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "continue"
        return "end"

    async def _supervisor_node(self, state: AgentState):
        msgs = state["messages"]
        # Convert all content to lower case for robust checking
        all_text = ""
        for m in msgs:
            if hasattr(m, "content") and m.content:
                all_text += " " + str(m.content).lower()
        
        # Count tool calls to prevent infinite loops
        tool_call_count = len([m for m in msgs if hasattr(m, "tool_calls") and m.tool_calls])
        
        # Check for key data points
        has_patient = "jordan lee" in all_text or "pt-1001" in all_text
        has_policy = "policy" in all_text or "requires_review" in all_text.lower()
        
        print(f"\n--- SUPERVISOR NODE ({len(msgs)} msgs, {tool_call_count} tool calls) ---")
        print(f"Status: patient={has_patient}, policy={has_policy}")
        
        # If we have the basics or have tried too many times, go to coordinator
        if (has_patient and has_policy) or tool_call_count >= 6:
            print("Decision: care_coordinator")
            return {"next": "care_coordinator"}
        
        print("Decision: triage_nurse")
        return {"next": "triage_nurse"}

    async def _triage_nurse_node(self, state: AgentState):
        print("--- TRIAGE NURSE NODE ---")
        sys = SystemMessage(content=(
            "You are a triage nurse. Use tools to gather facts for Jordan Lee (PT-1001).\n"
            "1. CALL patient_record(patient_id='PT-1001') if record is missing.\n"
            "2. CALL policy_check(request='MRI') for MRI policy.\n"
            "3. CALL appointment_slots for availability.\n"
            "DO NOT just talk. Use tools. When tools provide results, stop and let the supervisor handle it."
        ))
        ai_msg = await self.llm.bind_tools(self.tools).ainvoke([sys] + state["messages"])
        return {"messages": [ai_msg]}

    async def _care_coordinator_node(self, state: AgentState):
        print("--- CARE COORDINATOR NODE ---")
        sys = SystemMessage(content=(
            "You are a care coordinator. Review the gathered facts (patient Jordan Lee, MRI policy, slots).\n"
            "Write a clear 3-paragraph plan: Summary, Appointment Details, and Coverage/Instructions.\n"
            "Mention Jordan Lee by name and the MRI pre-authorization requirement specifically."
        ))
        response = await self.llm.ainvoke([sys] + state["messages"])
        return {"messages": [response]}

    async def process(self, message: str, history: List[BaseMessage]) -> dict:
        messages = history + [HumanMessage(content=message)]
        result = await self.graph.ainvoke({"messages": messages}, config={"recursion_limit": 100})
        return {"content": result["messages"][-1].content}

    async def astream_events(self, message: str, history: List[BaseMessage]) -> AsyncGenerator[Any, None]:
        # Initial Plan
        yield PlanEvent(steps=[
            {"id": "triage", "description": "Gathering patient information and checking policies", "status": "pending"},
            {"id": "coordination", "description": "Synthesizing care coordination plan", "status": "pending"},
        ])

        messages = history + [HumanMessage(content=message)]
        
        # We manually stream node-by-node for better status updates
        state = {"messages": messages, "next": ""}
        
        # 1. Triage Phase
        yield StatusEvent(step_id="triage", status="running", details="Starting triage process...")
        
        async for event in self.graph.astream_events(state, version="v1", config={"recursion_limit": 100}):
            kind = event["event"]
            
            # Catch token streams
            if kind == "on_chat_model_stream":
                metadata = event.get("metadata", {})
                node = metadata.get("langgraph_node")
                
                # DEBUG: Print metadata to trace node names in the graph
                # print(f"DEBUG: Node: {node}, Meta: {metadata}")
                
                # Only stream tokens from the care_coordinator node
                # Note: LangGraph often prefixes node names with the graph name or uses internal IDs
                # We'll check for the substring to be safe
                if node and ("care_coordinator" in node or node == "care_coordinator"):
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
            
            elif kind == "on_node_end":
                node = event["name"]
                if node == "triage_nurse":
                    # Update status after triage node finishes
                    yield StatusEvent(step_id="triage", status="running", details="Triage logic complete, checking supervisor...")
        
        yield StatusEvent(step_id="coordination", status="completed", details="Care plan complete.")
        yield MessageEvent(content="", is_final=True)

    def get_agent_info(self) -> dict:
        return {
            "id": "healthcare",
            "name": "Healthcare Coordinator",
            "description": "Orchestrates triage, policy checks, and care planning.",
            "type": "orchestrator"
        }
