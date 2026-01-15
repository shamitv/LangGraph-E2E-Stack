import asyncio
from typing import Dict, Any, List, AsyncGenerator
from langchain_core.messages import BaseMessage
from agent_demo_framework.agents.base_agent import BaseAgent
from agent_demo_framework.schemas.stream import PlanEvent, StatusEvent, MessageEvent, StepInfo

class MultiStepAgent(BaseAgent):
    """A mock agent that simulates a multi-step process with streaming updates."""
    
    def __init__(self):
        super().__init__("multistep")
        self.steps = [
            StepInfo(id="step1", description="Analyzing request context"),
            StepInfo(id="step2", description="Searching knowledge base"),
            StepInfo(id="step3", description="Synthesizing response"),
            StepInfo(id="step4", description="Final validation")
        ]
    
    async def process(self, message: str, history: List[BaseMessage]) -> Dict[str, Any]:
        """Legacy synchronous process method (fallback)."""
        # In a real implementation, this would accumulate the stream result
        return {
            "content": "This agent is optimized for streaming. Please use the streaming endpoint.",
            "metadata": {"agent": self.name}
        }
    
    async def astream_events(self, message: str, history: List[BaseMessage]) -> AsyncGenerator[Any, None]:
        """Stream events for the multi-step process."""
        
        # 1. Emit Plan
        yield PlanEvent(steps=self.steps)
        
        # 2. Execute Steps
        for step in self.steps:
            # Mark running
            yield StatusEvent(step_id=step.id, status="running")
            await asyncio.sleep(1.5) # Simulate work
            
            # Mark completed
            yield StatusEvent(step_id=step.id, status="completed", details=f"Completed {step.description}")
            await asyncio.sleep(0.5)
            
        # 3. Emit Final Message
        final_response = f"I have completed the {len(self.steps)} steps successfully. Your request '{message}' has been processed."
        yield MessageEvent(content=final_response, is_final=True)

    def get_agent_info(self) -> Dict[str, str]:
        return {
            "name": self.name,
            "description": "A simulation agent that performs multiple visible steps."
        }
