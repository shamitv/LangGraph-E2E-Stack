"""Base agent class for LangGraph agents."""
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from langchain_core.messages import BaseMessage


class BaseAgent(ABC):
    """Base class for all LangGraph agents."""
    
    def __init__(self, name: str):
        """Initialize the agent.
        
        Args:
            name: Name of the agent
        """
        self.name = name
    
    @abstractmethod
    async def process(self, message: str, history: List[BaseMessage]) -> Dict[str, Any]:
        """Process a message and return a response.
        
        Args:
            message: User message
            history: Conversation history
            
        Returns:
            Dictionary containing the response and metadata
        """
        pass
    
    @abstractmethod
    def get_agent_info(self) -> Dict[str, str]:
        """Get information about the agent.
        
        Returns:
            Dictionary containing agent name and description
        """
        pass
