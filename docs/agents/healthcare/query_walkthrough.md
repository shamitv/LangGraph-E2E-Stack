# Healthcare Agent Query Walkthrough (+ Data Agent)

**Date**: 2026-01-15
**Update**: Integrated **Data Agent** for simple queries.

## Summary
The **Information Assistant** (formerly Data Agent) successfully handles informational queries (e.g., patient lookup, allergies) with concise, direct answers, bypassing the complex Triage/Care Coordination workflow. Complex tasks (e.g., scheduling) default correctly to the Care Coordinators.

## Comparative Results

### Query 1: Data Agent vs Care Coordinator
**Query**: "Give me a summary of patient John Doe (MRN 12345)."
*   **Previous Behavior**: Care Coordinator drafted a formal plan.
*   **New Behavior**: **Information Assistant** provided a concise 4-line summary.
*   **Screenshot**: `img/query_1.png`

![Information Assistant - Patient Summary](img/query_1.png)

---

### Query 2: Allergies (Information Assistant)
**Query**: "What are the current allergies for Emily Chen...?"
*   **Observed**: Direct one-line text from Information Assistant.
*   **Screenshot**: `img/query_2.png`

![Information Assistant - Allergies](img/query_2.png)

---

### Query 3: Scheduling (Care Coordinator)
**Query**: "Find the next available cardiology appointment..."
*   **Observed**: Supervisor routed to Triage Nurse (Coordination path). Agent asked clarifying questions about site/preference.
*   **Screenshot**: `img/query_3.png`

![Care Coordinator - Scheduling](img/query_3.png)

---

### Query 4: Policy Check (Information Assistant)
**Query**: "Is a CT scan ... pre-authorized...?"
*   **Observed**: Information Assistant checked policy and returned strict "Yes/No/Review" status concisely.
*   **Screenshot**: `img/query_4.png`

![Information Assistant - Policy Check](img/query_4.png)

---

### Query 5: LLM Routing (Typo Handling)
**Query**: "What do we knwo about Noah" (Note the typo "knwo")
*   **Previous Behavior**: Regex failed to match "general" intent keywords; defaulted to Care Coordinator.
*   **New Behavior**: **LLM Router** correctly identified "general" intent despite the typo. Agent asked for clarification (Information Assistant style) without crashing.
*   **Screenshot**: `img/query_5.png`

---

### Query 6: Appointment Scheduling (Coordination)
**Query**: "Schedule a follow‑up appointment for patient Noah."
*   **Observed**: Supervisor routed to Triage Nurse, then Care Coordinator drafted a plan.
*   **Screenshot**: `img/query_6.png`

---
