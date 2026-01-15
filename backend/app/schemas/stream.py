from typing import List, Optional, Literal, Union
from pydantic import BaseModel, Field

from enum import Enum

class StreamEventType(str, Enum):
    """Types of events that can be streamed."""
    PLAN = "plan"
    STATUS = "status"
    MESSAGE = "message"
    ERROR = "error"

class StepInfo(BaseModel):
    """Information about a single step in a plan."""
    id: str
    description: str
    status: Literal["pending", "running", "completed", "failed"] = "pending"

class PlanEvent(BaseModel):
    """Event sent when the agent formulates a plan."""
    type: Literal["plan"] = "plan"
    steps: List[StepInfo]

class StatusEvent(BaseModel):
    """Event sent when a step's status changes."""
    type: Literal["status"] = "status"
    step_id: str
    status: Literal["pending", "running", "completed", "failed"]
    details: Optional[str] = None

class MessageEvent(BaseModel):
    """Event sent for standard chat messages (partial or complete)."""
    type: Literal["message"] = "message"
    content: str
    is_final: bool = False

class ErrorEvent(BaseModel):
    """Event sent when an error occurs."""
    type: Literal["error"] = "error"
    error: str

# Union type for all possible events
StreamEvent = Union[PlanEvent, StatusEvent, MessageEvent, ErrorEvent]
