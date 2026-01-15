import json
import os
from langchain_core.tools import tool
from ...core.config import settings

@tool("appointment_slots")
def appointment_slots(clinic: str, specialty: str, date_range: str = "next_7_days") -> str:
    """
    Return available appointment slots for a clinic and specialty within a date range.
    date_range examples: 'next_7_days', 'next_14_days'.
    """
    db_path = os.path.join(settings.DATA_DIR, "mock_db", "appointments.json")
    if not os.path.exists(db_path):
        return json.dumps({"error": f"Appointments database not found at {db_path}"}, indent=2)

    try:
        with open(db_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        return json.dumps({"error": f"Error reading appointments database: {e}"}, indent=2)

    entries = data.get("appointments", [])
    matches = [
        entry for entry in entries
        if entry.get("clinic") == clinic
        and entry.get("specialty") == specialty
        and entry.get("date_range") == date_range
    ]

    if matches:
        entry = matches[0]
        return json.dumps(
            {
                "clinic": clinic,
                "specialty": specialty,
                "date_range": date_range,
                "slots": entry.get("slots", []),
            },
            indent=2,
        )

    return json.dumps(
        {
            "clinic": clinic,
            "specialty": specialty,
            "date_range": date_range,
            "slots": [],
            "note": "No slots found for that combination.",
        },
        indent=2,
    )
