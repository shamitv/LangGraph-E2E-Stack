# Plan: Healthcare Care Coordinator Agent Integration

## 1. Overview
We will implement a `HealthcareAgent` inspired by the `healthcare_care_coordinator.py` example. This agent uses a supervisor-worker pattern to:
1.  **Triage**: Gather patient info, check coverage, and verify policies (`triage_nurse`).
2.  **Coordinate**: Synthesize a care plan (`care_coordinator`).

It will integrate with our existing:
-   **API**: `POST /api/v1/chat/stream` (SSE).
-   **UI**: Generic Chat Interface (supporting streaming events).
-   **Infrastructure**: `BaseAgent` class, `AgentFactory`, and `backend/agent_demo_framework/data` directory.

> [!IMPORTANT]
> **Scope Disclaimer**: This is a **basic Proof of Concept (POC)** implementation.
> -   It uses **mock data** (no real EMR integration).
> -   The `policy_check` is simplified for demonstration.
> -   It is **NOT** intended for real medical use or decision making.
> -   Authentication and detailed error handling are minimal.
> -   **Context Management**: Maintains simple raw message history; does not use advanced memory or summarization.

## 2. Architecture

### 2.1 Agent Structure (`backend/agent_demo_framework/agents/healthcare_agent.py`)
-   **Class**: `HealthcareAgent(BaseAgent)`
-   **Graph**: `StateGraph` with:
    -   `supervisor`: Routes to `triage_nurse`, `care_coordinator`, or `end`.
    -   `triage_nurse`: Calls tools (patient_record, policy_check, etc.).
    -   `care_coordinator`: Synthesizes final response.
    -   `tools`: `ToolNode` executing the actual tool logic.

### 2.2 Data Management
-   **Project Data**: Defaults to `d:\work\LangGraph-E2E-Demo\backend\agent_demo_framework\data`.
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
| `patient_record` | Hardcoded dict | `backend/agent_demo_framework/tools/healthcare/patient.py` |
| `appointment_slots` | Hardcoded dict | `backend/agent_demo_framework/tools/healthcare/scheduling.py` |
| `medication_info` | Hardcoded dict | `backend/agent_demo_framework/tools/healthcare/meds.py` |
| `coverage_check` | Hardcoded logic | `backend/agent_demo_framework/tools/healthcare/coverage.py` |
| `policy_check` | **Complex 2-phase LLM** | `backend/agent_demo_framework/tools/healthcare/policy.py` |

**Policy Check Tool Details**:
-   Reads `README.md` from `backend/agent_demo_framework/data/policies/`.
-   Uses LLM to select relevant policies.
-   Reads specific MD files.
-   Evaluates compliance.

## 4. Integration TO-DOs

### Phase 1: Setup & Data
- [x] Update `backend/agent_demo_framework/core/config.py` to add `DATA_DIR` setting (defaulting to package `data/`).
- [x] Create `backend/agent_demo_framework/agents/healthcare_agent.py`.
- [x] Create `backend/agent_demo_framework/tools/healthcare/` package.
- [x] Create `{DATA_DIR}/policies/` and populate with `README.md` + policy files (from example repo).
- [x] Register `HealthcareAgent` in `AgentFactory` (`backend/agent_demo_framework/agents/agent_factory.py`).

### Phase 2: Tool Implementation
- [x] Implement `patient_record`, `appointment_slots`, `medication_info`, `coverage_check`.
- [x] Implement `policy_check` logic:
    -   Dependency: `backend/agent_demo_framework/data/policies` path configuration.
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
- [x] Write a command-line script to run the agent in isolation (single prompt + streaming output) for quick validation.

### Phase 6: De-hardcode Agent Logic
- [x] Remove hardcoded patient references (`Jordan Lee`, `PT-1001`) from supervisor, triage, and care coordinator prompts.
- [x] Make triage tool calls conditional on user intent (e.g., only call `policy_check` for imaging requests).
- [x] Make plan step labels dynamic based on selected tools/actions.
- [x] Avoid fixed node-name filtering in streaming; derive target node(s) from config or graph metadata.
- [x] Make recursion limit configurable (settings/env). Keep hardcoded `100` as default.

## 5. UI Implications
-   No specific UI changes needed if generic streaming is robust.
-   The "Execution Plan" will naturally show the supervisor's transitions (e.g., Supervisor -> Triage -> Tools -> Care Coordinator).

## 6. Test Queries for Agent Validation

The following **20 queries** can be used to test the Healthcare Agent across its core capabilities (patient lookup, policy validation, coverage checks, appointment scheduling, and care-plan generation). Add these to your test suite or run them manually to verify correct behavior.

| # | Query |
|---|-------|
| 1 | "Give me a summary of patient **John Doe** (MRN 12345)." |
| 2 | "What are the current allergies for **Emily Chen**, MRN 67890?" |
| 3 | "Check if **aspirin** is covered for patient **Michael Patel** under his insurance plan." |
| 4 | "Is a **CT scan of the abdomen** a pre-authorized procedure for **Sarah Lee**?" |
| 5 | "Find the next available **cardiology** appointment for **David Kim** within the next two weeks." |
| 6 | "List all **controlled substances** policies that apply to **patient #1122**." |
| 7 | "Does **patient #4455** have any outstanding **MRI** pre-authorizations?" |
| 8 | "Create a care-plan for **Maria Gonzalez** with a focus on diabetes management and upcoming lab work." |
| 9 | "What is the copay amount for a **physical therapy** session for **John Doe**?" |
|10| "Validate that **patient #9988**'s insurance covers **home health nursing** services." |
|11| "Schedule a **telehealth** follow-up for **Emily Chen** on Thursday morning." |
|12| "Retrieve the most recent **lab results** for **Michael Patel**." |
|13| "Is a **flu vaccine** considered preventive and therefore covered for **Sarah Lee**?" |
|14| "Check whether **patient #3322** is eligible for a **weight-loss program** under their plan." |
|15| "Provide a list of **available orthopedic surgeons** for **David Kim** in the next month." |
|16| "Does the policy allow **off-label use** of **drug X** for **Maria Gonzalez**?" |
|17| "Summarize the **care coordination** steps needed for **John Doe** after his recent discharge." |
|18| "What documentation is required to obtain pre-authorization for a **knee replacement** for **Emily Chen**?" |
|19| "Verify that **patient #7777**'s plan covers **mental health counseling** sessions." |
|20| "Generate a discharge summary for **Michael Patel**, including medication changes and follow-up appointments." |

These queries exercise the agent's full workflow, ensuring that patient data retrieval, policy checks, scheduling, and care-plan synthesis all function as expected.

## 7. Mock Data Coverage for Queries 1–12

The following mock patient records are available in [backend/agent_demo_framework/data/mock_db/patients.json](../../../backend/agent_demo_framework/data/mock_db/patients.json) to support the first 12 queries:

- **John Doe (MRN 12345)** → `PT-12345`
- **Emily Chen (MRN 67890)** → `PT-67890`
- **Michael Patel** → `PT-3003`
- **Sarah Lee** → `PT-4455`
- **David Kim** → `PT-5566`
- **Patient #1122** → `PT-1122` (Avery Brooks)
- **Patient #4455** → `PT-4455` (Sarah Lee)
- **Maria Gonzalez** → `PT-7788`
- **Patient #9988** → `PT-9988` (Noah Williams)

Each record includes:
- Demographics, conditions, allergies, current meds, and insurance plan.
- `labs` entries to support query 12 (“most recent lab results”).

**Notes on scenario coverage**:
- Coverage queries (e.g., aspirin, copay, plan checks) are supported via the mock coverage matrix in [backend/agent_demo_framework/tools/healthcare/coverage.py](../../../backend/agent_demo_framework/tools/healthcare/coverage.py).
- Policy validation queries (e.g., imaging, controlled substances) are supported by policy files in `backend/agent_demo_framework/data/policies/` and the `policy_check` tool.
- Scheduling queries depend on `appointment_slots` in [backend/agent_demo_framework/tools/healthcare/scheduling.py](../../../backend/agent_demo_framework/tools/healthcare/scheduling.py). Mock cardiology slots are limited; when none are found, the agent will request location or date-range adjustments.
