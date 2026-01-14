#!/bin/bash
set -e

echo "🚀 Starting LangGraph E2E Demo Setup..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check for .env file
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating one from template..."
    echo "OPENAI_API_KEY=your-api-key-here" > .env
    echo "📝 Please edit .env and add your OpenAI API key"
    echo "   Then run this script again."
    exit 1
fi

# Check if OPENAI_API_KEY is set
source .env
if [ "$OPENAI_API_KEY" = "your-api-key-here" ]; then
    echo "⚠️  Please set your OPENAI_API_KEY in the .env file"
    exit 1
fi

echo "✅ Environment configured"

# Start services
echo "🐳 Starting Docker services..."
docker-compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are running
if docker ps | grep -q langgraph_backend; then
    echo "✅ Backend is running"
else
    echo "❌ Backend failed to start"
    docker-compose logs backend
    exit 1
fi

if docker ps | grep -q langgraph_frontend; then
    echo "✅ Frontend is running"
else
    echo "❌ Frontend failed to start"
    docker-compose logs frontend
    exit 1
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Access the application at:"
echo "  - Frontend: http://localhost:3000"
echo "  - Backend API: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/docs"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f"
echo ""
echo "To stop services:"
echo "  docker-compose down"
