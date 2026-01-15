"""API router initialization."""
from fastapi import APIRouter
from agent_demo_framework.api import chat

router = APIRouter()

# Include sub-routers
router.include_router(chat.router, prefix="/chat", tags=["chat"])
