# Plan: Multi-Turn Agent Status Updates via API

## 1. Problem Statement
Current agents execute all steps in a "black box" before returning the final response. For multi-step tasks (e.g., "perform 10 actions"), users need visibility into:
1.  **The Plan**: What steps the agent *intends* to take.
2.  **The Progress**: Real-time status updates as each step completes.

## 2. Proposed Architecture

We will transition from a synchronous REST API (`POST /chat`) to a **streaming architecture** using **Server-Sent Events (SSE)**.

### 2.1 Backend Changes

#### API Layer (`backend/app/api/chat.py`)
- **New Endpoint**: `POST /api/v1/chat/stream`
- **Mechanism**: StreamingResponse (FastAPI) yielding SSE-formatted data.
- **Event Protocol**:
  - `event: plan` -> Payload: list of steps `["Action 1", "Action 2", ...]`
  - `event: status` -> Payload: `{"step_index": 0, "status": "running"|"completed"|"failed", "details": "..."}`
  - `event: message` -> Payload: Final or intermediate partial text chunks.
  - `event: error` -> Payload: Error details.

#### Agent Layer
- Modify `BaseAgent` to support an `astream_events` or callback interface.
- **Agent State**: Track "planned_steps" and "current_step_index".
- **LangGraph Integration**: Use LangGraph's native streaming capabilities (`stream_mode="updates"` or custom callback handlers) to emit events during node transitions.

### 2.2 Frontend Changes

#### Service Layer (`frontend/src/services/api.ts`)
- Implement an `EventSource` or `fetch` with readable stream reader to consume the SSE endpoint.
- Parse standard SSE format (`id`, `event`, `data`).

#### UI Components
- **ChatMessage Component**:
  - Add support for a "structured thought process" view.
  - If a `plan` event is received, render a stepper or checklist.
  - Update the checklist items in real-time as `status` events arrive.

## 3. Implementation Steps

1.  **Define Event Schema**: Create shared types/schemas for `PlanEvent` and `StatusEvent`.
2.  **Backend Prototype**:
    - Create a mock "MultiStepAgent" that sleeps between steps to simulate work.
    - Implement the streaming endpoint.
3.  **Frontend Prototype**:
    - Build a `StepProgress` component.
    - Connect it to the streaming endpoint.
4.  **Integration**:
    - specific LangGraph callbacks to emission of these events.

## 4. Example Payload

**Draft Plan Event:**
```json
{
  "type": "plan",
  "steps": [
    {"id": "step1", "description": "Search for weather"},
    {"id": "step2", "description": "Calculate travel time"},
    {"id": "step3", "description": "Draft email"}
  ]
}
```

**Status Update Event:**
```json
{
  "type": "status",
  "step_id": "step1",
  "state": "completed",
  "result_summary": "Weather is sunny"
}
```

## 5. Implementation Status (2026-01-14)

### Completed
- [x] **Backend**: Defined `PlanEvent`, `StatusEvent`, `MessageEvent` schemas in `backend/app/schemas/stream.py`.
- [x] **Backend**: Implemented `MultiStepAgent` mock for testing.
- [x] **Backend**: Added `POST /api/v1/chat/stream` SSE endpoint in `backend/app/api/chat.py`.
- [x] **Frontend**: Created `streamService` with `fetch` and `TextDecoder` in `frontend/src/services/stream.ts`.
- [x] **Frontend**: Implemented `StepProgress` UI component.
- [x] **Frontend**: Integrated streaming into `ChatInterface`.

### Pending / Next Steps
1.  **LangGraph Integration**: Refactor real agents (e.g., `ConversationalAgent`) to use LangGraph's streaming callbacks to emit `status` events for real tool usage.
2.  **History Persistence**: Ensure the streaming endpoint correctly loads and saves conversation history to the database (currently mocked/TODO in `chat.py`).
3.  **Error Recovery**: Handle stream interruptions and reconnection logic in the frontend service.
