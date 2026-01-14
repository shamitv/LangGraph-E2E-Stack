"""Simple conversational agent using LangGraph."""
from typing import Dict, Any, List, TypedDict, Annotated, Sequence
import operator
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage
from langchain.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from app.agents.base_agent import BaseAgent
from app.core.config import settings
from app.schemas.stream import PlanEvent, StatusEvent, MessageEvent, StepInfo
from typing import AsyncGenerator
import json



class AgentState(TypedDict):
    """State for the conversational agent."""
    messages: Annotated[Sequence[BaseMessage], operator.add]


class ConversationalAgent(BaseAgent):
    """A simple conversational agent using LangGraph."""
    
    def __init__(self):
        """Initialize the conversational agent."""
        super().__init__("conversational")
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL_NAME,
            temperature=0.7,
            openai_api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_API_BASE
        ) if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY.strip() else None
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph state graph.
        
        Returns:
            Compiled state graph
        """
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("chat", self._chat_node)
        
        # Set entry point
        workflow.set_entry_point("chat")
        
        # Add edge to end
        workflow.add_edge("chat", END)
        
        return workflow.compile()
    
    async def _chat_node(self, state: AgentState) -> Dict[str, Any]:
        """Chat node that processes messages.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with response
        """
        if self.llm is None:
            # Fallback response if no API key configured
            return {
                "messages": [AIMessage(content="Hello! I'm a demo agent. Please configure your OpenAI API key to enable full functionality.")]
            }
        
        messages = state["messages"]
        response = await self.llm.ainvoke(messages)
        return {"messages": [response]}
    
    async def process(self, message: str, history: List[BaseMessage]) -> Dict[str, Any]:
        """Process a message and return a response.
        
        Args:
            message: User message
            history: Conversation history
            
        Returns:
            Dictionary containing the response and metadata
        """
        # Add system message if this is the first message
        messages = []
        if not history:
            messages.append(SystemMessage(content="You are a helpful AI assistant. Be concise and friendly."))
        
        # Add conversation history
        messages.extend(history)
        
        # Add current message
        messages.append(HumanMessage(content=message))
        
        # Run the graph
        result = await self.graph.ainvoke({"messages": messages})
        
        # Extract response
        last_message = result["messages"][-1]
        
        return {
            "content": last_message.content,
            "metadata": {
                "agent": self.name,
                "model": settings.OPENAI_MODEL_NAME if self.llm else "demo"
            }
        }
    
    
    async def astream_events(self, message: str, history: List[BaseMessage]) -> AsyncGenerator[Any, None]:
        """Stream events for the conversational agent."""
        
        # 1. Emit Initial Plan
        # For a simple conversation, the plan is just "Process Request"
        steps = [StepInfo(id="process", description="Process Request", status="running")]
        yield PlanEvent(steps=steps)
        yield StatusEvent(step_id="process", status="running")
        
        # 2. Prepare Messages
        messages = []
        if not history:
            messages.append(SystemMessage(content="You are a helpful AI assistant. Be concise and friendly."))
        messages.extend(history)
        messages.append(HumanMessage(content=message))
        
        # 3. Stream from LLM
        if self.llm:
            accumulated_content = ""
            try:
                # Use astream instead of ainvoke to get chunks
                # We need to extract the underlying string chunk
                async for chunk in self.llm.astream(messages):
                     content = chunk.content
                     if content:
                         accumulated_content += content
                         yield MessageEvent(content=content, is_final=False)
                
                # 4. Finalize
                yield StatusEvent(step_id="process", status="completed", details="Response generated")
                # Send one last event to confirm completion/save state if needed
                yield MessageEvent(content="", is_final=True)
                
            except Exception as e:
                yield StatusEvent(step_id="process", status="failed", details=str(e))
                yield MessageEvent(content=f"Error: {str(e)}", is_final=True)
                
        else:
            # Demo mode fallback
            demo_text = "I am a demo agent. Please configure your OpenAI API key."
            yield MessageEvent(content=demo_text, is_final=True)
            yield StatusEvent(step_id="process", status="completed")

    def get_agent_info(self) -> Dict[str, str]:
        """Get information about the agent.
        
        Returns:
            Dictionary containing agent name and description
        """
        return {
            "name": self.name,
            "description": f"A simple conversational agent powered by LangGraph and {settings.OPENAI_MODEL_NAME}"
        }
