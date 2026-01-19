"""Agent factory for creating and managing agents."""
from typing import Dict
from agent_demo_framework.agents.base_agent import BaseAgent
from agent_demo_framework.agents.conversational_agent import ConversationalAgent
from agent_demo_framework.agents.multistep_agent import MultiStepAgent
from agent_demo_framework.agents.healthcare_agent import HealthcareAgent
from agent_demo_framework.agents.po_preapproval_agent import POPreApprovalAgent


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
            "default": "po_preapproval",
            "conversational": "conversational",
            "multistep": "multistep",
            "healthcare": "healthcare",
            "po_preapproval": "po_preapproval",
        }
        
        agent_key = agent_map.get(agent_type, "conversational")
        
        # Create agent if it doesn't exist
        if agent_key not in cls._agents:
            if agent_key == "conversational":
                cls._agents[agent_key] = ConversationalAgent()
            elif agent_key == "multistep":
                cls._agents[agent_key] = MultiStepAgent()
            elif agent_key == "healthcare":
                cls._agents[agent_key] = HealthcareAgent()
            elif agent_key == "po_preapproval":
                cls._agents[agent_key] = POPreApprovalAgent()
        
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
