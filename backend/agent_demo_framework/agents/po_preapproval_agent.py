from typing import List, AsyncGenerator, Any, TypedDict, Annotated, Literal, Dict
import json
import re
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage, ToolMessage
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from .base_agent import BaseAgent
from ..schemas.stream import PlanEvent, StatusEvent, MessageEvent
from ..core.config import settings
from ..tools.po_tools import ALL_PO_TOOLS

# Define state
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    next: str
    shared_memory: Dict[str, Any] # The "Global Memory" for the case

class POPreApprovalAgent(BaseAgent):
    """
    Agentic PO Pre-approval System Agent.
    Orchestrates validation, context gathering, and policy checks for Purchase Orders.
    """
    
    def __init__(self):
        super().__init__("po_preapproval")
        self.tools = ALL_PO_TOOLS
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
        builder.add_node("context_gatherer", self._context_gatherer_node)
        builder.add_node("rule_engine", self._rule_engine_node)
        builder.add_node("decision_maker", self._decision_maker_node)
        builder.add_node("general_assistant", self._general_assistant_node)
        builder.add_node("human_review", self._human_review_node)
        builder.add_node("tools", self.tool_node)
        
        builder.set_entry_point("supervisor")
        
        # Routing from supervisor
        builder.add_conditional_edges(
            "supervisor",
            lambda x: x["next"],
            {
                "context_gatherer": "context_gatherer",
                "rule_engine": "rule_engine",
                "decision_maker": "decision_maker",
                "general_assistant": "general_assistant",
                "human_review": "human_review",
                "end": END
            }
        )

        builder.add_edge("general_assistant", END)
        builder.add_edge("human_review", END) # In a real HITL, this might route back or suspend
        
        # Context Gatherer -> Tools or Supervisor
        builder.add_conditional_edges(
            "context_gatherer",
            self._should_use_tools,
            {
                "tools": "tools",
                "next": "supervisor"
            }
        )

        # Rule Engine -> Tools or Supervisor
        builder.add_conditional_edges(
            "rule_engine",
            self._should_use_tools,
            {
                "tools": "tools",
                "next": "supervisor"
            }
        )
        
        # Decision Maker -> Tools (HITL) or End
        builder.add_conditional_edges(
            "decision_maker",
             self._should_use_tools,
             {
                 "tools": "tools",
                 "next": "supervisor" # If tool called, go to supervisor -> human_review
             }
        )
        
        builder.add_edge("tools", "supervisor")
        
        return builder.compile()

    # ... (skipping unchanged methods) ...

    async def _supervisor_node(self, state: AgentState):
        shared_mem = state.get("shared_memory", {})
        print(f"--- SUPERVISOR NODE (Memory Keys: {list(shared_mem.keys())}) ---")
        
        # 0. Initial Intent Check
        if not shared_mem:
             # ... (existing intent logic) ...
             messages = state["messages"]
             sys = SystemMessage(content=(
                "You are a routing supervisor.\n"
                "Classify the user's input into one of two categories:\n"
                "1. 'GENERAL': Greetings, asking for help, general questions about capabilities.\n"
                "2. 'PO_REQUEST': Requesting to submit, validate, or check a Purchase Order/Vendor/Budget.\n"
                "Return ONLY the category name."
            ))
             ai_msg = await self.llm.ainvoke([sys] + messages)
             intent = ai_msg.content.strip()
             print(f"DEBUG: Routing Decision: {intent}")
             
             if "GENERAL" in intent:
                 return {"next": "general_assistant"}
        
        # 1. New Case -> Gather Context
        if not shared_mem.get("context_gathered"):
            print("Decision: context_gatherer")
            return {"next": "context_gatherer"}
        
        # 2. Context Done -> Run Rules
        if not shared_mem.get("rules_checked"):
            print("Decision: rule_engine")
            return {"next": "rule_engine"}
        
        # 3. Rules Done -> Make Decision
        # Check if decision was already made but resulted in a tool call (HITL)
        messages = state["messages"]
        last_msg = messages[-1]
        
        if isinstance(last_msg, ToolMessage) and last_msg.name == "request_human_review":
             print("Decision: human_review (triggered by tool)")
             return {"next": "human_review"}

        if not shared_mem.get("decision_made"):
             print("Decision: decision_maker")
             return {"next": "decision_maker"}
             
        return {"next": "end"}

    # ... (skipping context_gatherer, rule_engine) ...

    async def _decision_maker_node(self, state: AgentState):
        print("--- DECISION MAKER NODE ---")
        
        # Update memory to say we attempted a decision
        current_mem = state.get("shared_memory", {}).copy()
        current_mem["decision_made"] = True
        
        sys = SystemMessage(content=(
            "You are the Decision Maker Agent.\n"
            "Review all tool outputs (Vendor status, Policy rules, Restricted lists, Budget).\n"
            "- If any BLOCK severity rule matches (e.g. Restricted List, Sanctions), output DENIED.\n"
            "- If WARN severity (e.g. Concentration Risk), call 'request_human_review'.\n" 
            "- Otherwise APPROVE.\n"
            "Provide a clear justification.\n"
            "If calling 'request_human_review', provide the reason and context."
        ))
        
        ai_msg = await self.llm.bind_tools(self.tools).ainvoke([sys] + state["messages"])
        return {"messages": [ai_msg], "shared_memory": current_mem}

    async def _human_review_node(self, state: AgentState):
        """Node to handle the HITL state."""
        print("--- HUMAN REVIEW NODE ---")
        return {"messages": [AIMessage(content="**STATUS**: Workflow paused for Human Review. A supervisor has been notified.")]}

    # ... (skipping process) ...

    async def astream_events(self, message: str, history: List[BaseMessage]) -> AsyncGenerator[Any, None]:
        # Update Plan
        yield PlanEvent(steps=[
            {"id": "context", "description": "Gathering Context (Vendor, Budget, Contracts)", "status": "pending"},
            {"id": "rules", "description": "Applying Policy & Compliance Rules", "status": "pending"},
            {"id": "decision", "description": "Final Decision & Audit", "status": "pending"}
        ])

        messages = history + [HumanMessage(content=message)]
        inputs = {"messages": messages, "next": "", "shared_memory": {}}
        
        yield StatusEvent(step_id="context", status="running", details="Initializing workflow...")

        async for event in self.graph.astream_events(inputs, version="v1", config={"recursion_limit": 20}):
            kind = event["event"]
            
            if kind == "on_chat_model_stream":
                metadata = event.get("metadata", {})
                node = metadata.get("langgraph_node")
                
                # Stream content
                if node in ["decision_maker", "general_assistant", "human_review"]:
                     content = event["data"]["chunk"].content
                     if content:
                        yield MessageEvent(content=content, is_final=False)

            elif kind == "on_tool_start":
                tool_name = event["name"]
                # Map tool calls
                if tool_name in ["vendor_lookup", "budget_check", "contract_search", "vendor_exposure"]:
                    yield StatusEvent(step_id="context", status="running", details=f"Calling {tool_name}...")
                elif tool_name in ["policy_get", "restricted_list_match", "sanctions_screen", "approval_matrix"]:
                    yield StatusEvent(step_id="context", status="completed", details="Context loaded.")
                    yield StatusEvent(step_id="rules", status="running", details=f"Checking {tool_name}...")
                elif tool_name == "audit_log_append":
                     yield StatusEvent(step_id="rules", status="completed", details="Rules evaluated.")
                     yield StatusEvent(step_id="decision", status="running", details="Finalizing decision...")
                elif tool_name == "request_human_review":
                     yield StatusEvent(step_id="decision", status="running", details="Requesting Human Review...")

            elif kind == "on_node_start":
                node = event["name"]
                if node == "decision_maker":
                     yield StatusEvent(step_id="rules", status="completed", details="Rules evaluated.")
                     yield StatusEvent(step_id="decision", status="running", details="Drafting outcome...")
                elif node == "general_assistant":
                    yield StatusEvent(step_id="context", status="completed", details="General query detected.")
                    yield StatusEvent(step_id="rules", status="completed", details="Skipped.")
                    yield StatusEvent(step_id="decision", status="completed", details="Providing info.")
                elif node == "human_review":
                    yield StatusEvent(step_id="decision", status="completed", details="See Output.")

        yield StatusEvent(step_id="decision", status="completed", details="Case closed.")
        yield MessageEvent(content="", is_final=True)

        yield StatusEvent(step_id="decision", status="completed", details="Case closed.")
        yield MessageEvent(content="", is_final=True)

    def get_agent_info(self) -> dict:
        return {
            "id": "po_preapproval",
            "name": "PO Pre-approval Agent",
            "description": "Validates POs against policies, restricted lists, and budgets.",
            "type": "agentic_process"
        }
