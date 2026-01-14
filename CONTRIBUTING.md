# Contributing to LangGraph E2E Demo

Thank you for your interest in contributing to LangGraph E2E Demo! This document provides guidelines and instructions for contributing.

## Getting Started

1. Fork the repository
2. Clone your fork locally
3. Create a new branch for your feature or bug fix
4. Make your changes
5. Test your changes
6. Submit a pull request

## Development Setup

See the [README.md](README.md) for detailed setup instructions.

## Code Style

### Python (Backend)

- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Write docstrings for all functions and classes
- Keep functions small and focused

### TypeScript/React (Frontend)

- Use TypeScript for all new code
- Follow React best practices
- Use functional components with hooks
- Keep components small and reusable

## Adding New Agents

To add a new agent:

1. Create a new file in `backend/app/agents/` (e.g., `my_agent.py`)
2. Inherit from `BaseAgent` class
3. Implement required methods: `process()` and `get_agent_info()`
4. Register your agent in `agent_factory.py`
5. Add tests for your agent

Example:

```python
from app.agents.base_agent import BaseAgent
from typing import Dict, Any, List
from langchain.schema import BaseMessage

class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__("my_agent")
    
    async def process(self, message: str, history: List[BaseMessage]) -> Dict[str, Any]:
        # Your agent logic here
        return {
            "content": "Response from my agent",
            "metadata": {"agent": self.name}
        }
    
    def get_agent_info(self) -> Dict[str, str]:
        return {
            "name": self.name,
            "description": "Description of my agent"
        }
```

## Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## Submitting Changes

1. Ensure all tests pass
2. Update documentation if needed
3. Commit your changes with clear, descriptive messages
4. Push to your fork
5. Create a pull request with a clear description of your changes

## Code Review Process

All submissions require review. We use GitHub pull requests for this purpose.

## Questions?

Feel free to open an issue for any questions or concerns.
