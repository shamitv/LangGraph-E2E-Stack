# Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Browser                             │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTP/WebSocket
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                      React Frontend                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Components:                                              │  │
│  │  - ChatInterface (Main UI)                               │  │
│  │  - ChatMessage (Message Display)                         │  │
│  │                                                           │  │
│  │  Services:                                               │  │
│  │  - API Service (Axios)                                   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  Port: 3000                                                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ REST API
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                      FastAPI Backend                             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  API Layer:                                               │  │
│  │  - /api/v1/chat/chat (POST)                              │  │
│  │  - /api/v1/chat/agents (GET)                             │  │
│  │  - /health (GET)                                         │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Core:                                                    │  │
│  │  - Configuration Management                              │  │
│  │  - CORS Middleware                                       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  Port: 8000                                                      │
└────────┬───────────────────────────────┬────────────────────────┘
         │                               │
         │                               │
         ▼                               ▼
┌────────────────────┐         ┌────────────────────────┐
│  LangGraph Agents  │         │  PostgreSQL Database   │
│                    │         │                        │
│  - BaseAgent       │         │  Tables:               │
│  - Conversational  │         │  - conversations       │
│    Agent           │         │  - messages            │
│  - Agent Factory   │         │  - agent_executions    │
│                    │         │                        │
│  LangChain/OpenAI  │         │  Port: 5432            │
└────────────────────┘         └────────────────────────┘
```

## Data Flow

User types message → ChatInterface → API Service → 
POST /api/v1/chat/chat → FastAPI → AgentFactory → 
ConversationalAgent → LangGraph → OpenAI API → 
Response → Database (optional) → Frontend
