import json
from langchain_core.tools import tool

@tool("coverage_check")
def coverage_check(insurance_plan: str, service: str) -> str:
    """
    Return mock coverage details: copay, pre-auth, limitations for a given insurance plan and service.
    """
    plan = insurance_plan.strip().upper()
    svc = service.strip().lower()

    # Mock rules
    matrix = {
        "ACME-HMO-SILVER": {
            "primary_care_visit": {"copay": "$25", "preauth_required": False},
            "specialist_visit": {"copay": "$50", "preauth_required": False},
            "mri": {"copay": "$150", "preauth_required": True},
            "controller_inhaler_refill": {"copay": "$10", "preauth_required": False},
        },
        "ACME-PPO-GOLD": {
            "primary_care_visit": {"copay": "$20", "preauth_required": False},
            "specialist_visit": {"copay": "$40", "preauth_required": False},
            "mri": {"copay": "$100", "preauth_required": True},
        },
    }

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
