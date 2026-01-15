import json
import os
from langchain_core.tools import tool
from ...core.config import settings

@tool("patient_record")
def patient_record(patient_id: str) -> str:
    """
    Retrieve patient demographics, conditions, allergies, current meds, insurance plan,
    and preferred clinic details.
    """
    db_path = os.path.join(settings.DATA_DIR, "mock_db", "patients.json")
    if not os.path.exists(db_path):
        return f"Error: Patient database not found at {db_path}"
    
    # Normalization
    raw_id = str(patient_id).strip().upper()
    # Try to extract PT- if missing (common if user just types 1001)
    if not raw_id.startswith("PT-") and raw_id.isdigit():
        target_id = f"PT-{raw_id}"
    else:
        target_id = raw_id

    try:
        print(f"DEBUG: patient_record tool called with ID: {target_id} (original: {patient_id})")
        with open(db_path, "r", encoding="utf-8") as f:
            records = json.load(f)
    except Exception as e:
        print(f"DEBUG: Error reading patient database: {e}")
        return f"Error reading patient database: {e}"
        
    if target_id in records:
        print(f"DEBUG: Found record for {target_id}")
        return json.dumps(records[target_id], indent=2)
    
    print(f"DEBUG: Record NOT found for {patient_id}")
    return f"Patient '{patient_id}' not found. Available IDs: {', '.join(records.keys())}"
