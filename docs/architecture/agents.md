# Agents

This document describes the AI agents currently implemented in the LangGraph E2E Demo and provides a guide on how to add new agents.

## Current Agents

### ConversationalAgent

**Type**: `conversational` (Default)

The `ConversationalAgent` is a general-purpose chatbot designed for open-ended interaction. 

- **Implementation**: `backend/agent_demo_framework/agents/conversational_agent.py`
- **Frameworks**: LangGraph, LangChain, OpenAI
- **Configuration**: 
  - Uses `OPENAI_MODEL_NAME` (default: `gpt-3.5-turbo`) defined in `.env`.
  - Uses `OPENAI_API_BASE` (default: `https://api.openai.com/v1`) for API requests.
- **Behavior**:
  - Maintains conversation history.
  - Returns a fallback message if no API key is configured.
  - Can be extended with custom tools or more complex graph flows.

## How to Add a New Agent

To add a new agent to the system, follow these steps:

### 1. Create the Agent Class

Create a new file in `backend/agent_demo_framework/agents/` (e.g., `my_custom_agent.py`). Your class must inherit from `BaseAgent` and implement the required methods.

```python
from typing import Dict, Any, List
from langchain_core.messages import BaseMessage
from agent_demo_framework.agents.base_agent import BaseAgent

class MyCustomAgent(BaseAgent):
    def __init__(self):
        super().__init__("custom_agent_name")
        # Initialize your LLM, tools, or graph here
    
    async def process(self, message: str, history: List[BaseMessage]) -> Dict[str, Any]:
        # Implement your agent logic here
        return {
            "content": "Response from your custom agent",
            "metadata": {
                "agent": self.name
            }
        }
    
    def get_agent_info(self) -> Dict[str, str]:
        return {
            "name": self.name,
            "description": "Description of what this agent does"
        }
```

### 2. Register in Agent Factory

Update `backend/agent_demo_framework/agents/agent_factory.py` to include your new agent.

1.  Import your new agent class.
2.  Update `get_agent` to return an instance of your agent when requested.

```python
# ... imports
from agent_demo_framework.agents.my_custom_agent import MyCustomAgent

class AgentFactory:
    # ...
    
    @classmethod
    def get_agent(cls, agent_type: str = "default") -> BaseAgent:
        # ... existing map
        agent_map = {
            "default": "conversational",
            "conversational": "conversational",
            "custom": "custom_agent_name", # Add mapping
        }
        
        agent_key = agent_map.get(agent_type, "conversational")
        
        if agent_key not in cls._agents:
            if agent_key == "conversational":
                cls._agents[agent_key] = ConversationalAgent()
            elif agent_key == "custom_agent_name": # Instantiate
                cls._agents[agent_key] = MyCustomAgent()
        
        return cls._agents[agent_key]
```

### 3. Usage

You can now use your agent by attempting to chat with a specific agent type (if the frontend supports selecting agents) or by changing the default mapping in the factory.
