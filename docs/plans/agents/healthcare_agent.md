# Plan: Healthcare Care Coordinator Agent Integration

## 1. Overview
We will implement a `HealthcareAgent` inspired by the `healthcare_care_coordinator.py` example. This agent uses a supervisor-worker pattern to:
1.  **Triage**: Gather patient info, check coverage, and verify policies (`triage_nurse`).
2.  **Coordinate**: Synthesize a care plan (`care_coordinator`).

It will integrate with our existing:
-   **API**: `POST /api/v1/chat/stream` (SSE).
-   **UI**: Generic Chat Interface (supporting streaming events).
-   **Infrastructure**: `BaseAgent` class, `AgentFactory`, and `data/` directory.

> [!IMPORTANT]
> **Scope Disclaimer**: This is a **basic Proof of Concept (POC)** implementation.
> -   It uses **mock data** (no real EMR integration).
> -   The `policy_check` is simplified for demonstration.
> -   It is **NOT** intended for real medical use or decision making.
> -   Authentication and detailed error handling are minimal.
> -   **Context Management**: Maintains simple raw message history; does not use advanced memory or summarization.

## 2. Architecture

### 2.1 Agent Structure (`backend/app/agents/healthcare_agent.py`)
-   **Class**: `HealthcareAgent(BaseAgent)`
-   **Graph**: `StateGraph` with:
    -   `supervisor`: Routes to `triage_nurse`, `care_coordinator`, or `end`.
    -   `triage_nurse`: Calls tools (patient_record, policy_check, etc.).
    -   `care_coordinator`: Synthesizes final response.
    -   `tools`: `ToolNode` executing the actual tool logic.

### 2.2 Data Management
-   **Project Data**: Defaults to `d:\work\LangGraph-E2E-Demo\data`.
    -   **Configurable**: Can be overridden via `DATA_DIR` environment variable (in `.env` or system env).
-   **Policies**: `{DATA_DIR}/policies/` will store the markdown policy files used by the `policy_check` tool.
-   **Mock Databases**: Move hardcoded dictionaries (patients, slots, meds) into JSON files in `{DATA_DIR}/mock_db/` for cleaner separation.

### 2.3 Streaming Integration
-   Implement `astream_events`:
    -   Emit `PlanEvent`: "Planning care coordination..."
    -   Emit `StatusEvent`:
        -   "Triage Nurse: Checking policies..."
        -   "Triage Nurse: Checking appointment slots..."
        -   "Care Coordinator: Drafting plan..."
    -   Emit `MessageEvent`: Real-time token streaming from the final `care_coordinator` response.

## 3. Tool Migration

| Tool | Source Implementation | Target Implementation |
| :--- | :--- | :--- |
| `patient_record` | Hardcoded dict | `backend/app/tools/healthcare/patient.py` |
| `appointment_slots` | Hardcoded dict | `backend/app/tools/healthcare/scheduling.py` |
| `medication_info` | Hardcoded dict | `backend/app/tools/healthcare/meds.py` |
| `coverage_check` | Hardcoded logic | `backend/app/tools/healthcare/coverage.py` |
| `policy_check` | **Complex 2-phase LLM** | `backend/app/tools/healthcare/policy.py` |

**Policy Check Tool Details**:
-   Reads `README.md` from `data/policies/`.
-   Uses LLM to select relevant policies.
-   Reads specific MD files.
-   Evaluates compliance.

## 4. Integration TO-DOs

### Phase 1: Setup & Data
- [x] Update `backend/app/core/config.py` to add `DATA_DIR` setting (defaulting to project root `data/`).
- [x] Create `backend/app/agents/healthcare_agent.py`.
- [x] Create `backend/app/tools/healthcare/` package.
- [x] Create `{DATA_DIR}/policies/` and populate with `README.md` + policy files (from example repo).
- [x] Register `HealthcareAgent` in `AgentFactory` (`backend/app/agents/agent_factory.py`).

### Phase 2: Tool Implementation
- [x] Implement `patient_record`, `appointment_slots`, `medication_info`, `coverage_check`.
- [x] Implement `policy_check` logic:
    -   Dependency: `data/policies` path configuration.
    -   Dependency: Secondary `LLM` instance for policy analysis (re-use main LLM config).

### Phase 3: Graph & Supervisor
- [x] Implement `HealthcareAgent._build_graph`.
- [x] Implement `supervisor` node logic.
- [x] Implement `triage_nurse` node logic (bind tools).
- [x] Implement `care_coordinator` node logic (final output).

### Phase 4: Streaming
- [x] Implement `astream_events` in `HealthcareAgent`.
- [x] Ensure specific node activities (e.g., "Calling policy_check") emit visible `StatusEvent`s.

### Phase 5: Testing
- [ ] Write a command-line script to run the agent in isolation (single prompt + streaming output) for quick validation.

## 5. UI Implications
-   No specific UI changes needed if generic streaming is robust.
-   The "Execution Plan" will naturally show the supervisor's transitions (e.g., Supervisor -> Triage -> Tools -> Care Coordinator).

