import random
from typing import Dict, List, Optional
from langchain_core.tools import tool

# T1: VendorMaster.lookup(vendor_id)
@tool("vendor_lookup")
def vendor_lookup(vendor_id: str) -> Dict:
    """Look up vendor profile, onboarding status, and risk tier."""
    # Mock data
    if vendor_id == "V12345":
        return {
            "vendor_id": "V12345",
            "legal_name": "Acme IT Services",
            "onboarded": True,
            "risk_tier": "High",
            "last_due_diligence": "2024-05-15"
        }
    elif vendor_id == "V99999":
        return {
            "vendor_id": "V99999",
            "legal_name": "Unknown Entity",
            "onboarded": False,
            "risk_tier": "Critical",
        }
    return {"error": "Vendor not found"}

# T2: Sanctions.screen(vendor_legal_name, tax_id)
@tool("sanctions_screen")
def sanctions_screen(vendor_legal_name: str, tax_id: Optional[str] = None) -> Dict:
    """Screen vendor against international sanctions lists."""
    if "BadActor" in vendor_legal_name:
        return {"status": "MATCH", "list": "OFAC SDNs", "confidence": 0.95}
    return {"status": "CLEAN", "checked_at": "2026-01-19T10:00:00Z"}

# T4: Budget.get_cost_center_state(cost_center, period)
@tool("budget_check")
def budget_check(cost_center: str, period: str = "2026-Q1") -> Dict:
    """Check budget remaining and committed spend for a cost center."""
    return {
        "cost_center": cost_center,
        "details": {
            "total_budget": 500000,
            "committed": 420000,
            "remaining": 80000,
            "currency": "USD"
        }
    }

# T5: SpendAnalytics.get_vendor_exposure(vendor_id, period)
@tool("vendor_exposure")
def vendor_exposure(vendor_id: str, period: str = "2026-Q1") -> Dict:
    """Get spend-to-date and concentration for a vendor."""
    return {
        "vendor_id": vendor_id,
        "spend_qtd": 150000,
        "concentration_percent": 38.5,  # High concentration demo
        "category": "IT Services"
    }

# T6: ContractRepo.search(vendor_id, category, region)
@tool("contract_search")
def contract_search(vendor_id: str, category: str = "IT Services", region: str = "US") -> List[Dict]:
    """Search for valid contracts."""
    if vendor_id == "V12345":
        return [{
            "contract_id": "C-2025-001",
            "title": "Master Services Agreement",
            "expiry": "2027-12-31"
        }]
    return []

# T10: PolicyStore.get_policy_pack(bu, category, region)
@tool("policy_get")
def policy_get(bu: str = "Global", category: str = "IT", region: str = "US") -> Dict:
    """Retrieve the active policy pack and thresholds."""
    return {
        "policy_pack_id": "PP-2026-01-A",
        "version": "3.4.1",
        "rules": [
            {"id": "R-BLK-001", "description": "Vendor matched restricted list", "severity": "BLOCK"},
            {"id": "R-BLK-002", "description": "Vendor not onboarded", "severity": "BLOCK"},
            {"id": "R-WRN-001", "description": "Vendor concentration > 35%", "severity": "WARN"},
            {"id": "R-WRN-002", "description": "Requester limit exceeded", "severity": "WARN"}
        ]
    }

# T11: RestrictedLists.match(entity, list_type)
@tool("restricted_list_match")
def restricted_list_match(entity: str, list_type: str = "BlockedVendors") -> Dict:
    """Check if an entity appears on a specific restricted list."""
    if entity == "V12345":
        return {
            "match": True,
            "list_type": list_type,
            "version": "2026-01-10",
            "reason": "Previous performance issues - Do not use"
        }
    return {"match": False, "list_type": list_type, "version": "2026-01-10"}

# T12: Approvals.get_matrix(bu, category, amount)
@tool("approval_matrix")
def approval_matrix(bu: str, category: str, amount: float) -> Dict:
    """Determine the required approver chain."""
    return {
        "matrix_id": "AM-IT-TIER2",
        "steps": [
            {"role": "Manager", "limit": 10000},
            {"role": "Director", "limit": 100000},
            {"role": "VP", "limit": 500000}
        ]
    }

# T13: AuditLog.append(event)
@tool("audit_log_append")
def audit_log_append(event_type: str, details: Dict) -> Dict:
    """Append an event to the immutable audit log."""
    return {
        "status": "success",
        "event_id": f"evt_{random.randint(1000,9999)}",
        "timestamp": "2026-01-19T10:00:05Z",
        "hash": "0x123abc..."
    }

ALL_PO_TOOLS = [
    vendor_lookup,
    sanctions_screen,
    budget_check,
    vendor_exposure,
    contract_search,
    policy_get,
    restricted_list_match,
    approval_matrix,
    audit_log_append
]
