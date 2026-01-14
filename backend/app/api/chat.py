"""Chat API endpoints."""
import uuid
from fastapi import APIRouter, HTTPException
from langchain.schema import HumanMessage, AIMessage
from app.schemas import ChatRequest, ChatResponse
from app.agents import AgentFactory

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process a chat message using the specified agent.
    
    Args:
        request: Chat request with message and session info
        
    Returns:
        Chat response from the agent
    """
    try:
        # Generate or use existing session ID
        session_id = request.session_id or str(uuid.uuid4())
        
        # Get the appropriate agent
        agent = AgentFactory.get_agent(request.agent_type or "default")
        
        # For now, we're not persisting history - this would be added later
        # In a production system, you'd fetch conversation history from the database
        history = []
        
        # Process the message
        result = await agent.process(request.message, history)
        
        return ChatResponse(
            message=result["content"],
            session_id=session_id,
            agent_type=request.agent_type or "default",
            metadata=result.get("metadata", {})
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents")
async def list_agents():
    """List all available agents.
    
    Returns:
        Dictionary of available agents and their information
    """
    try:
        agents = AgentFactory.list_agents()
        return {"agents": agents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
