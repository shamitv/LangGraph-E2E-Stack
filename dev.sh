#!/bin/bash
# Development helper script for LangGraph E2E Demo

show_help() {
    echo "LangGraph E2E Demo - Development Helper"
    echo ""
    echo "Usage: ./dev.sh [command]"
    echo ""
    echo "Commands:"
    echo "  start       - Start all services with Docker Compose"
    echo "  stop        - Stop all services"
    echo "  restart     - Restart all services"
    echo "  logs        - Show logs from all services"
    echo "  backend     - Start backend only (local dev)"
    echo "  frontend    - Start frontend only (local dev)"
    echo "  db          - Start database only"
    echo "  migrate     - Run database migrations"
    echo "  clean       - Clean up containers and volumes"
    echo "  help        - Show this help message"
    echo ""
}

case "$1" in
    start)
        echo "🚀 Starting all services..."
        docker-compose up -d
        ;;
    stop)
        echo "🛑 Stopping all services..."
        docker-compose down
        ;;
    restart)
        echo "♻️  Restarting all services..."
        docker-compose restart
        ;;
    logs)
        echo "📋 Showing logs (Ctrl+C to exit)..."
        docker-compose logs -f
        ;;
    backend)
        echo "🐍 Starting backend in local dev mode..."
        cd backend
        if [ ! -d "venv" ]; then
            echo "Creating virtual environment..."
            python -m venv venv
        fi
        source venv/bin/activate
        pip install -r requirements.txt
        uvicorn agent_demo_framework.main:app --reload --host 0.0.0.0 --port 8000
        ;;
    frontend)
        echo "⚛️  Starting frontend in local dev mode..."
        cd frontend
        if [ ! -d "node_modules" ]; then
            echo "Installing dependencies..."
            npm install
        fi
        npm run dev
        ;;
    db)
        echo "🗄️  Starting database only..."
        docker-compose up -d postgres
        ;;
    migrate)
        echo "🔄 Running database migrations..."
        cd backend
        alembic upgrade head
        ;;
    clean)
        echo "🧹 Cleaning up..."
        docker-compose down -v
        echo "✅ Cleanup complete"
        ;;
    help|*)
        show_help
        ;;
esac
