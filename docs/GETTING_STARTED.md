# Getting Started Guide

## Quick Start (5 minutes)

### Prerequisites
- Docker and Docker Compose installed
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/shamitv/LangGraph-E2E-Demo.git
   cd LangGraph-E2E-Demo
   ```

2. **Configure your API key**
   ```bash
   cp .env.example .env
   # Edit .env and replace 'your-api-key-here' with your actual OpenAI API key
   ```

3. **Start the application**
   ```bash
   ./start.sh
   ```

4. **Access the application**
   - Open your browser to http://localhost:3000
   - Start chatting with the AI agent!

## Manual Setup (Without Docker)

### Backend Setup

1. **Install Python dependencies**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Setup database**
   ```bash
   # Start PostgreSQL (adjust connection string in .env if needed)
   alembic upgrade head
   ```

4. **Start backend**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. **Install Node dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Defaults should work if backend is on localhost:8000
   ```

3. **Start frontend**
   ```bash
   npm run dev
   ```

## Verify Installation

### Test Backend
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy"}
```

### Test API Documentation
Visit http://localhost:8000/docs for interactive API documentation

### Test Frontend
Visit http://localhost:3000 and send a test message

## Common Issues

### Port Already in Use
If ports 3000, 8000, or 5432 are already in use:
- Change ports in docker-compose.yml or
- Stop conflicting services

### Database Connection Error
- Ensure PostgreSQL is running
- Check DATABASE_URL in backend/.env
- Verify database exists: `psql -U postgres -c "CREATE DATABASE langgraph_demo;"`

### OpenAI API Error
- Verify your API key is correct
- Check you have credits in your OpenAI account
- Ensure OPENAI_API_KEY is set in .env

## Next Steps

1. Read the [Architecture documentation](ARCHITECTURE.md)
2. Explore the API at http://localhost:8000/docs
3. Check [CONTRIBUTING.md](../CONTRIBUTING.md) to add your own agents
4. Customize the UI in `frontend/src/components/`

## Development Commands

```bash
# Start all services
./dev.sh start

# View logs
./dev.sh logs

# Stop services
./dev.sh stop

# Run database migrations
./dev.sh migrate

# Clean up
./dev.sh clean
```

## Environment Variables Reference

### Backend (.env)
- `OPENAI_API_KEY` - Your OpenAI API key (required)
- `DATABASE_URL` - PostgreSQL connection string
- `API_V1_STR` - API version prefix (default: /api/v1)
- `BACKEND_CORS_ORIGINS` - Allowed CORS origins

### Frontend (.env)
- `VITE_API_URL` - Backend API URL (default: http://localhost:8000/api/v1)

## Support

- Issues: https://github.com/shamitv/LangGraph-E2E-Demo/issues
- Documentation: See docs/ folder
