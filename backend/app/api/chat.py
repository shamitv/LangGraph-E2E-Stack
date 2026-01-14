"""Chat API endpoints."""
import uuid
from fastapi import APIRouter, HTTPException
from langchain.messages import HumanMessage, AIMessage
from app.schemas import ChatRequest, ChatResponse
from app.schemas import ChatRequest, ChatResponse
from app.agents import AgentFactory
from fastapi.responses import StreamingResponse
import json
import logging

logger = logging.getLogger(__name__)

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


@router.post("/stream")
async def stream_chat(request: ChatRequest):
    """Process a chat message with streaming updates."""
    
    async def event_generator():
        try:
            # Generate session ID if not provided
            session_id = request.session_id or str(uuid.uuid4())
            agent = AgentFactory.get_agent(request.agent_type or "default")
            
            # Check if agent supports streaming
            if not hasattr(agent, "astream_events"):
                 # Fallback for non-streaming agents
                 history = []
                 result = await agent.process(request.message, history)
                 yield f"event: message\ndata: {json.dumps({'type': 'message', 'content': result['content'], 'is_final': True})}\n\n"
                 return

            # Use streaming interface
            # TODO: Fetch real history from DB
            history = []
            
            async for event in agent.astream_events(request.message, history):
                # Serialize event to JSON
                # Provide explicit mapping or rely on pydantic .model_dump_json()
                event_type = event.type
                payload = event.model_dump_json()
                yield f"event: {event_type}\ndata: {payload}\n\n"
                
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield f"event: error\ndata: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
            
    return StreamingResponse(event_generator(), media_type="text/event-stream")


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
