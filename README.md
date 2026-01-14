# LangGraph E2E Demo

A full-stack demonstration of LangGraph agents with a React chatbot UI and FastAPI backend. This project showcases how to build an end-to-end AI agent system with modern web technologies.

## 🏗️ Architecture

This project consists of four main components:

1. **React UI** - Modern chatbot interface built with React, TypeScript, and Vite
2. **FastAPI Backend** - Async API layer for agent communication
3. **LangGraph Agents** - AI agents powered by LangGraph and LangChain
4. **PostgreSQL Database** - Conversation and execution tracking

## 📁 Project Structure

```
LangGraph-E2E-Demo/
├── frontend/                 # React UI
│   ├── src/
│   │   ├── components/      # React components (ChatInterface, ChatMessage)
│   │   ├── services/        # API service layer
│   │   └── types/           # TypeScript type definitions
│   ├── package.json
│   └── vite.config.ts
│
├── backend/                 # FastAPI Backend
│   ├── app/
│   │   ├── agents/         # LangGraph agent implementations
│   │   ├── api/            # FastAPI routes
│   │   ├── core/           # Core configuration
│   │   ├── db/             # Database configuration
│   │   ├── models/         # SQLAlchemy models
│   │   └── schemas/        # Pydantic schemas
│   ├── alembic/            # Database migrations
│   └── requirements.txt
│
└── docker-compose.yml      # Docker orchestration
```

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose (recommended)
- OR:
  - Python 3.11+
  - Node.js 20+
  - PostgreSQL 15+

### Option 1: Using Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/shamitv/LangGraph-E2E-Demo.git
   cd LangGraph-E2E-Demo
   ```

2. **Set up environment variables**
   ```bash
   # Create .env file in the root directory
   echo "OPENAI_API_KEY=your-api-key-here" > .env
   ```

3. **Start all services**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Option 2: Local Development

#### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

5. **Start PostgreSQL**
   ```bash
   # Make sure PostgreSQL is running on localhost:5432
   # Or update DATABASE_URL in .env
   ```

6. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

7. **Start the backend server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

#### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Defaults to http://localhost:8000/api/v1
   ```

4. **Start the development server**
   ```bash
   npm run dev
   ```

5. **Access the application**
   - Open http://localhost:3000 in your browser

## 🛠️ Technology Stack

### Frontend
- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Axios** - HTTP client
- **Lucide React** - Icons

### Backend
- **FastAPI** - Modern async web framework
- **LangGraph** - Agent orchestration
- **LangChain** - LLM framework
- **SQLAlchemy** - ORM
- **Alembic** - Database migrations
- **PostgreSQL** - Database
- **Pydantic** - Data validation

## 📚 API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

- `POST /api/v1/chat/chat` - Send a message to the agent
- `GET /api/v1/chat/agents` - List available agents
- `GET /health` - Health check

## 🤖 Agents

The project includes a conversational agent powered by LangGraph:

- **ConversationalAgent** - A general-purpose chatbot using GPT-3.5-turbo

You can extend this by creating new agents in `backend/app/agents/` that inherit from `BaseAgent`.

## 🗄️ Database Schema

The database includes tables for:

- **conversations** - Chat sessions
- **messages** - Individual chat messages
- **agent_executions** - Agent execution tracking

To create a new migration:
```bash
cd backend
alembic revision --autogenerate -m "Description of changes"
alembic upgrade head
```

## 🔧 Configuration

### Backend Environment Variables

Create `backend/.env` with:

```env
OPENAI_API_KEY=your-api-key-here
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/langgraph_demo
API_V1_STR=/api/v1
PROJECT_NAME=LangGraph E2E Demo
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
```

### Frontend Environment Variables

Create `frontend/.env` with:

```env
VITE_API_URL=http://localhost:8000/api/v1
```

## 🧪 Development

### Running Tests

```bash
# Backend tests (to be added)
cd backend
pytest

# Frontend tests (to be added)
cd frontend
npm test
```

### Code Style

- Backend follows PEP 8 style guide
- Frontend uses ESLint with TypeScript rules

## 📝 License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

## 🙏 Acknowledgments

- Built with [LangGraph](https://github.com/langchain-ai/langgraph)
- Powered by [FastAPI](https://fastapi.tiangolo.com/)
- UI built with [React](https://react.dev/)
