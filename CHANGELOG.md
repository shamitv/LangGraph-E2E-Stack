# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2026-01-14

### Security
- Updated `aiohttp` from 3.9.1 to 3.13.3 to fix:
  - HTTP Parser zip bomb vulnerability (CVE affecting versions <= 3.13.2)
  - Denial of Service in malformed POST requests (CVE affecting versions < 3.9.4)
  - Directory traversal vulnerability (CVE affecting versions >= 1.0.5, < 3.9.2)
- Updated `fastapi` from 0.109.0 to 0.109.1 to fix:
  - Content-Type Header ReDoS vulnerability
- Updated `python-multipart` from 0.0.6 to 0.0.18 to fix:
  - DoS via malformed multipart/form-data boundary (CVE affecting versions < 0.0.18)
  - Content-Type Header ReDoS vulnerability (CVE affecting versions <= 0.0.6)

## [1.0.0] - 2026-01-14

### Added
- Initial repository setup
- React UI with TypeScript and Vite
  - ChatInterface component with modern design
  - ChatMessage component for displaying messages
  - API service layer for backend communication
- FastAPI backend with async support
  - RESTful API endpoints for chat
  - CORS configuration for frontend integration
  - Pydantic schemas for request/response validation
- LangGraph agents module
  - BaseAgent abstract class
  - ConversationalAgent using GPT-3.5-turbo
  - AgentFactory for managing agent instances
- Database schema with SQLAlchemy
  - Conversations table for chat sessions
  - Messages table for chat history
  - Agent executions table for tracking
  - Alembic migrations setup
- Docker configuration
  - docker-compose.yml for easy deployment
  - Dockerfiles for backend and frontend
  - PostgreSQL service configuration
- Documentation
  - Comprehensive README with setup instructions
  - CONTRIBUTING.md for contributor guidelines
  - Environment configuration examples
- Development tools
  - start.sh script for quick setup
  - dev.sh script for development helpers
