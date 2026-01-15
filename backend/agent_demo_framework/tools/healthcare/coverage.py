import json
import os
from langchain_core.tools import tool
from ...core.config import settings

@tool("coverage_check")
def coverage_check(insurance_plan: str, service: str) -> str:
    """
    Return mock coverage details: copay, pre-auth, limitations for a given insurance plan and service.
    """
    plan = insurance_plan.strip().upper()
    svc = service.strip().lower()
    db_path = os.path.join(settings.DATA_DIR, "mock_db", "coverage.json")
    if not os.path.exists(db_path):
        return json.dumps({"error": f"Coverage database not found at {db_path}"}, indent=2)

    try:
        with open(db_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        return json.dumps({"error": f"Error reading coverage database: {e}"}, indent=2)

    matrix = data.get("plans", {})
    if plan not in matrix:
        return json.dumps({"insurance_plan": plan, "service": service, "note": "Unknown plan in mock coverage DB."}, indent=2)

    # Simple mapping
    if "mri" in svc or "imaging" in svc:
        key = "mri"
    elif "specialist" in svc or "pulmon" in svc or "neuro" in svc:
        key = "specialist_visit"
    elif "visit" in svc or "primary" in svc:
        key = "primary_care_visit"
    elif "inhaler" in svc or "refill" in svc:
        key = "controller_inhaler_refill"
    else:
        key = "primary_care_visit"

    return json.dumps({"insurance_plan": plan, "service": service, **matrix[plan].get(key, {})}, indent=2)
