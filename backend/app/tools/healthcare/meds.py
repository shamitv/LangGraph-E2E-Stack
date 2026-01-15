import json
import os
from langchain_core.tools import tool
from ...core.config import settings

@tool("medication_info")
def medication_info(drug: str) -> str:
    """
    Return high-level medication info (class, common use, notes).
    """
    db_path = os.path.join(settings.DATA_DIR, "mock_db", "meds.json")
    if not os.path.exists(db_path):
        return json.dumps({"error": f"Medication database not found at {db_path}"}, indent=2)

    try:
        with open(db_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        return json.dumps({"error": f"Error reading medication database: {e}"}, indent=2)

    k = drug.strip().lower()
    if k in data:
        return json.dumps({"item": drug, **data[k]}, indent=2)
    return json.dumps({"item": drug, "note": "Not found in mock medication database."}, indent=2)
