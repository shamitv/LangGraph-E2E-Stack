# Agentic Procurement PO Pre‑Approval System — Detailed Specification (with Trace UI)

> **Purpose:** A non‑finance demo scenario that mirrors “pre‑trade checks” in capability: context gathering, deterministic rule evaluation, limit/concentration checks, restricted lists, evidence chasing, exception approvals, explainability, and immutable auditability — **plus a UI-visible agent/tool “trace”** showing *how* decisions were reached.

---

## 1) Goals and Non‑Goals

### Goals
- Validate a **Purchase Order (PO)** *before* it is released/committed in ERP.
- Combine **agentic context & evidence gathering** with a **deterministic policy engine**.
- Classify results into **HARD BLOCK / SOFT WARN / INFO** and drive **HITL** approval flows.
- Produce **Explainability** that cites rules, thresholds, evidence, and computations.
- Produce an **Audit Pack**: immutable record of inputs, tools, checks, outputs, and timestamps.
- Provide a **Trace UI** that shows:  
  *“Denied because Vendor X matched Restricted List Y (version Z). Agents used Tool A, Tool B to gather context; rules R‑123 and R‑455 fired; approval/override policy required; final decision denied.”*

### Non‑Goals (demo scope)
- Replacing ERP (SAP/Oracle/etc.). This is a **gate** integrating via API/webhook.
- Negotiating pricing or optimizing supplier selection.
- Full contract authoring; only **contract/evidence retrieval** and **term validation**.

---

## 2) Primary Entities and Minimal Data Model

### Core Objects
- **Case**: the orchestration wrapper around a PO validation event (unique `case_id`).
- **Purchase Order (PO)**: the object being validated.
- **Vendor/Supplier**: identity + onboarding + compliance posture.
- **Requester**: employee who submits PO.
- **Approver(s)**: per approval matrix and exception taxonomy.
- **Policy Pack**: versioned rules and thresholds.
- **Evidence Pack**: documents + extracted fields + provenance.
- **Decision Record**: outcome, reason codes, conditions.
- **Audit Pack**: immutable log + snapshots + hash chain.

### PO Input Schema (minimum)
- `po_id`, `business_unit`, `cost_center`, `requester_id`, `vendor_id`
- `ship_to`, `bill_to`, `region/country`
- Line items: `sku/description`, `category`, `qty`, `unit_price`, `currency`, `line_total`
- `po_total`, `payment_terms`, `delivery_terms`, `incoterms` (optional)
- `contract_ref` (optional), `quote_refs[]`, `sow_ref` (optional), `justification_text`
- `requested_delivery_date`, `project_code` (optional), `gl_code` (optional)

### Vendor Profile (minimum)
- Legal name, tax ID, address, bank details (and last change timestamp)
- Onboarding status, approved vendor flag
- Risk tier + last due diligence date
- Sanctions/PEP screening status + last screened timestamp
- Restricted categories/regions flags

---

## 3) End‑to‑End Workflow

1. **PO Submitted** → system creates a **Case** (`case_id`) and pins an initial **PO snapshot**.
2. **Context Gather**  
   - Requester identity & entitlements  
   - Vendor profile & compliance posture  
   - Budgets & current exposure/state  
   - Applicable contracts/terms
3. **Evidence Gather**  
   - Retrieve attachments & referenced docs  
   - Detect missing mandatory artifacts (quote/SOW/security questionnaire/etc.)
4. **Restricted List Checks**  
   - Vendor/region/item/user restrictions (versioned lists)
5. **Policy & Rule Evaluation**  
   - Run deterministic rules → `BLOCK` / `WARN` / `INFO`
6. **Limit & Concentration Checks**  
   - PO caps, period caps, vendor/category concentration thresholds
7. **Decision Draft**  
   - Proposed outcome + remediation checklist
8. **Human‑in‑the‑Loop**  
   - Approvers review summary + evidence + trace + checks
9. **Finalize**  
   - Decision signed; policy/list versions pinned; audit pack generated
10. **ERP Integration**  
   - If approved → release PO to ERP  
   - Else → return with required changes/remediation steps

---

## 4) Agent Architecture

### 4.1 Agents (recommended)
1. **Orchestrator / Case Manager (Supervisor)**
2. **Identity & Entitlement Agent**
3. **Vendor Risk & Compliance Agent**
4. **Contract & Terms Agent**
5. **Budget & Exposure Agent**
6. **Policy & Rules Engine Agent (Deterministic)**
7. **Evidence & Document Agent**
8. **Exception & Approval Routing Agent**
9. **Explainability & Remediation Agent**
10. **Audit Pack & Compliance Logging Agent (Immutable Recorder)**
11. **Trace & Provenance Agent** *(powers “Trace UI”)*

> The **Trace & Provenance Agent** is not a “reasoning agent” that changes outcomes; it **structures** and **renders** trace data from shared memory: tool calls, intermediate facts, rule hits, evidence pointers, approvals, and final decision.

---

## 5) Tools (Concrete “Tool1…ToolN” for Trace)

For demo realism, define named tools with stable IDs:

- **T1: VendorMaster.lookup(vendor_id)** → vendor profile, onboarding, risk tier
- **T2: Sanctions.screen(vendor_legal_name, tax_id)** → match/no-match + list version
- **T3: ERP.get_po(po_id)** / **ERP.update_po(po_id, patch)** → PO retrieval/update
- **T4: Budget.get_cost_center_state(cost_center, period)** → budget remaining, committed spend
- **T5: SpendAnalytics.get_vendor_exposure(vendor_id, period)** → spend-to-date, concentration
- **T6: ContractRepo.search(vendor_id, category, region)** → contract candidates
- **T7: ContractRepo.fetch(contract_id)** → contract doc + metadata
- **T8: DocStore.fetch(doc_ref)** / **DocStore.put(file)** → evidence retrieval/upload
- **T9: DocExtract.extract(doc, schema)** → extracted structured fields + confidence
- **T10: PolicyStore.get_policy_pack(bu, category, region)** → rule pack + thresholds version
- **T11: RestrictedLists.match(entity, list_type)** → matches + list version
- **T12: Approvals.get_matrix(bu, category, amount)** → approver chain
- **T13: AuditLog.append(event)** → immutable event log entry (hash chained)

These tools are intentionally modular so the trace can show: *which tool was called, by which agent, and what evidence it produced*.

---

## 6) Memory Design

### 6.1 Shared Global Memory (Case Blackboard)
Structured, versioned, and append‑only. Required sections:

1. **Case metadata:** `case_id`, status, timestamps, SLA timers
2. **PO snapshot(s):** immutable `po_snapshot_v1`, `po_snapshot_v2`…
3. **Context graph:** requester profile, vendor profile, contract refs, exposure metrics
4. **Evidence registry:** doc list, doc types, checksums, extraction outputs, provenance
5. **Restricted list results:** matches, list versions, match rationale
6. **Rule evaluation results:** rule hits, severities, computed values, policy version pinned
7. **Limit checks:** caps/thresholds, period definitions, source systems
8. **Workflow:** approval chain, exception routes, assigned approvers
9. **Human actions:** comments, approvals, overrides, reason codes
10. **Trace ledger:** tool calls, agent steps, intermediate facts, timings
11. **Audit stream pointer:** hash chain head, export bundle location

**Global memory invariants**
- No deletes; only append new versions.
- Every fact stored includes:
  - `source_tool`, `source_agent`, `timestamp`, `confidence` (if extracted), `evidence_ref`

---

### 6.2 Per‑Agent Memory (Private)
Each agent maintains:
- **Ephemeral:** current task state, intermediate reasoning scratchpad, retries
- **Long‑lived (optional):** patterns/templates (non‑case specific)

*(Outcome‑affecting decisions must always be backed by shared memory facts, not private memory.)*

---

## 7) Required Capabilities Mapping (Explicit)

### 7.1 Context gathering (profiles, entitlements, current exposure/state)
- **Agents:** Identity & Entitlement; Vendor Risk; Budget & Exposure; Contract & Terms
- **Tools:** T1, T4, T5, T6, T7
- **Stored in global memory:** requester entitlements, vendor profile, exposure metrics, contract constraints
- **UI:** Context tab + Trace step showing tool calls and derived facts

### 7.2 Rule evaluation (hard blocks vs soft warnings; configurable policies)
- **Agents:** Policy & Rules Engine (deterministic)
- **Tools:** T10 (policy pack)
- **Stored:** rule hits with `severity`, `rule_id`, computed values, evidence pointers
- **UI:** Checks tab; every rule card links to Trace segment that produced it

### 7.3 Limit checks (caps, thresholds, concentration-like constraints)
- **Agents:** Budget & Exposure + Rules Engine
- **Tools:** T4, T5, T10
- **Stored:** metrics + thresholds + period definitions; concentration ratios
- **UI:** Limits tab + “what‑if” simulator (demo)

### 7.4 Restricted lists (blocked vendors/regions/items/users)
- **Agents:** Vendor Risk + Rules Engine
- **Tools:** T11 (restricted list), optionally T2 (sanctions list)
- **Stored:** match details + list version, match rationale
- **UI:** Restrictions tab + Trace view highlights the match as the decisive cause (if BLOCK)

### 7.5 Document evidence (missing artifacts → agent requests them)
- **Agents:** Evidence & Document
- **Tools:** T8, T9
- **Stored:** required docs checklist, missing items, extracted fields with provenance
- **UI:** Evidence tab + Trace shows which doc checks failed and why

### 7.6 Exceptions + approvals (human-in-the-loop routing)
- **Agents:** Exception & Approval Routing
- **Tools:** T12
- **Stored:** approval chain, exception routes, SoD constraints, SLA timers
- **UI:** Approvals tab + Trace shows routing decision and policy triggers

### 7.7 Explainability (why approved/blocked + how to remediate)
- **Agents:** Explainability & Remediation
- **Inputs:** rule hits + evidence refs + computed values
- **Outputs:** narratives per audience + remediation checklist
- **UI:** Decision page + “Fix this” checklist + Trace-backed citations

### 7.8 Audit pack (immutable log of inputs, checks, outputs, timestamps)
- **Agents:** Audit Pack & Compliance Logging
- **Tools:** T13
- **Stored:** append-only event ledger + hash chain + export bundle
- **UI:** Audit tab + Trace tab (trace is part of audit evidence)

---

## 8) Policy System (Configurable + Versioned)

### 8.1 Rule structure
Each rule has:
- `rule_id`, `title`, `description`
- `applies_to`: BU/category/region/vendor_tier
- `severity`: `BLOCK | WARN | INFO`
- `logic`: deterministic expression over facts
- `required_evidence`: doc types
- `remediation`: steps + links
- `owner`: Finance/Procurement/Legal/Security
- `version`, `effective_dates`

### 8.2 Example rule catalog (demo-friendly)
- **BLOCK:** Vendor not onboarded
- **BLOCK:** Vendor matched restricted list
- **BLOCK:** Missing mandatory SOW for Services PO > threshold
- **WARN:** Requester approval limit exceeded → route
- **WARN:** Vendor concentration > 35% category spend (QTD)
- **WARN:** Payment terms exceed allowed maximum
- **INFO:** Price variance vs last 3 purchases > X%

---

## 9) UI Specification (with Trace)

### 9.1 Screens

#### A) Case Inbox (Procurement/Finance)
- Rows: case_id, vendor, amount, BU/category, status, SLA, **highest severity**, **trace badge**
- Filters: BLOCK/WARN only; vendor risk tier; category; age; assigned-to
- Search: vendor, requester, PO ID, contract ID

#### B) Case Detail (tabs)
**Header**: PO summary + status + next action + top 1–3 reasons

Tabs:
1. **Overview**
2. **Context**
3. **Checks**
4. **Limits**
5. **Restrictions**
6. **Evidence**
7. **Approvals**
8. **Decision**
9. **Audit**
10. **Trace** ✅ *(required)*

---

### 9.2 Trace Tab (Core Requirement)

#### What the Trace must answer (explicitly)
- **What happened?** (ordered timeline)
- **Which agent did what?**
- **Which tools were called?** (Tool IDs: T1…T13)
- **What facts were produced?** (with provenance)
- **Which checks fired?** (rule IDs)
- **What evidence supports the decision?** (doc pointers + list versions)
- **Why denied/approved?** (decision provenance tree)
- **How to remediate?** (actionable steps linked to failed checks)

#### Trace UI Components

##### 1) Timeline View (Event Stream)
A vertical timeline with expandable events. Each event shows:
- agent name
- tool call (if any)
- concise summary (no secrets)
- links to artifacts (evidence doc, restricted list entry, rule hit record)
- latency, status (success/fail), retry count

**Example trace (denied due to restricted list match):**
- `09:14:02` **Case created** (Orchestrator)
- `09:14:06` **T1 VendorMaster.lookup** (Vendor Risk Agent) → `vendor_onboarded=true`
- `09:14:08` **T11 RestrictedLists.match(vendor)** (Vendor Risk Agent) → **match=true**, list=“BlockedVendors”, version=**2026‑01‑10**
- `09:14:12` **T10 PolicyStore.get_policy_pack** (Rules Engine Agent) → policy_pack=**v3.4.1**
- `09:14:14` **Rule R‑BLK‑001 fired** (Rules Engine Agent) → severity=**BLOCK**
- `09:14:16` **Decision drafted: DENY** (Orchestrator)
- `09:14:18` **Explanation generated** (Explainability Agent)
- `09:14:21` **Audit event appended** (Audit Agent via T13)

##### 2) Agent Graph View (Call Graph)
A node graph:
- Nodes: agents
- Edges: messages/tasks
- Clicking an edge reveals:
  - input facts used (IDs)
  - output facts written (IDs)
  - tool calls invoked

##### 3) Decision Provenance Tree (“Why” View)
A tree expanding from final decision to supporting facts:

**DENY**
- because **Rule R‑BLK‑001 (Vendor blocked)**
  - derived from **RestrictedLists.match result**
    - list: BlockedVendors v2026‑01‑10
    - matched entity: vendor_id=V12345
    - evidence: `restricted_list_match_id=RL‑8891`
  - policy pack: v3.4.1
- remediation:
  - “Select different vendor” OR “Request vendor unblock review (Legal/Compliance)”

This view must be clickable:
- click the match → open the exact match record and list version
- click the rule → open rule definition and parameters used

##### 4) Tool Call Detail Drawer
Selecting a tool call shows:
- tool id/version, environment (prod/mock)
- request parameters (redacted as needed)
- response summary + link to raw response (if allowed)
- facts written to shared memory
- errors/retries

##### 5) Replay / Determinism Controls
- “Re-run checks with pinned versions” (policy/list versions locked)
- “Simulate edits” (what-if) creates `po_snapshot_vN` and adds a **trace branch**

---

### 9.3 Trace Integration Across Other Tabs
- In **Checks**, each rule hit has **Show trace** → highlights producing events.
- In **Restrictions**, each match has **Show trace** + list version details.
- In **Decision**, “Top reasons” are clickable and open the provenance tree at that node.

---

## 10) Decisioning Outcomes

- **Auto‑Approve** (no WARN/BLOCK; only INFO)
- **Approve with Conditions** (WARN only; conditions logged)
- **Route for Approval** (WARN + matrix requires human)
- **Return for Changes** (missing docs / fixable issues)
- **Hard Deny / Block** (restricted list match, sanctions hit, SoD violation)

Overrides:
- Only authorized roles; only override‑eligible rules.
- Must include reason code + justification doc + expiry (if conditional).
- Trace must show override event, who did it, and what rule was overridden.

---

## 11) Audit Pack (Immutable + Trace‑Backed)

### 11.1 Audit ledger requirements
- Append-only event log:
  - PO snapshots (hash)
  - evidence checksums
  - policy pack + restricted list versions (hash)
  - tool call records (IDs, timestamps, statuses)
  - rule execution results
  - human actions (approvals/overrides)
  - final decision record
- Tamper evidence:
  - hash chain: each event includes hash of previous
  - exportable as JSONL + manifest

### 11.2 Export bundle
- `manifest.json` (hashes, versions, pointers)
- `po_snapshots.json`
- `rule_hits.json`
- `restricted_matches.json`
- `evidence_registry.json`
- `trace_events.jsonl`
- `approvals.json`
- optional PDF “audit report” summarizing the above

---

## 12) Demo Script (Trace‑first)

### Scenario: PO denied due to restricted vendor
1. Submit PO for “IT Services” worth $120k.
2. Vendor Risk Agent calls **T11** → match found (BlockedVendors v2026‑01‑10).
3. Rules Engine pins policy pack and fires **R‑BLK‑001** (BLOCK).
4. Orchestrator drafts **DENY**.
5. Explainability generates remediation steps.
6. UI shows **DENIED** + clickable reason → opens **Trace** to the exact tool call and match record.

### Variant: replace vendor and re-run
1. Edit vendor → new PO snapshot.
2. Replay pinned checks; now vendor is clean but missing SOW → “Return for changes”.
3. Upload SOW → re-run; now routes to Finance approval (requester limit exceeded).
4. Trace shows branch/replay and how outcomes changed.

---

## Appendix A: Minimal Trace Event Schema (illustrative)

- `event_id`
- `timestamp`
- `case_id`
- `actor_type`: `agent | human | system`
- `actor_id`: agent name or user id
- `event_type`: `tool_call | rule_hit | decision_transition | evidence_update | approval_action`
- `tool_id` (optional)
- `inputs_ref[]` (pointers to facts/docs)
- `outputs_ref[]`
- `status`: `success | fail | retry`
- `latency_ms`
- `policy_versions`: policy pack + restricted list versions in effect
- `hash_prev`, `hash_this` (for chain)

---

*End of specification.*
