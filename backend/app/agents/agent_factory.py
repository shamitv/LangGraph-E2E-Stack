"""Agent factory for creating and managing agents."""
from typing import Dict
from app.agents.base_agent import BaseAgent
from app.agents.conversational_agent import ConversationalAgent


class AgentFactory:
    """Factory for creating and managing different types of agents."""
    
    _agents: Dict[str, BaseAgent] = {}
    
    @classmethod
    def get_agent(cls, agent_type: str = "default") -> BaseAgent:
        """Get an agent instance by type.
        
        Args:
            agent_type: Type of agent to retrieve
            
        Returns:
            Agent instance
        """
        # Map agent types to implementations
        agent_map = {
            "default": "conversational",
            "conversational": "conversational",
        }
        
        agent_key = agent_map.get(agent_type, "conversational")
        
        # Create agent if it doesn't exist
        if agent_key not in cls._agents:
            if agent_key == "conversational":
                cls._agents[agent_key] = ConversationalAgent()
        
        return cls._agents[agent_key]
    
    @classmethod
    def list_agents(cls) -> Dict[str, Dict[str, str]]:
        """List all available agents.
        
        Returns:
            Dictionary of agent information
        """
        # Ensure all agents are initialized
        cls.get_agent("conversational")
        
        return {
            agent_type: agent.get_agent_info()
            for agent_type, agent in cls._agents.items()
        }
