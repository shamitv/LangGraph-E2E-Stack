import json
from langchain_core.tools import tool

@tool("appointment_slots")
def appointment_slots(clinic: str, specialty: str, date_range: str = "next_7_days") -> str:
    """
    Return available appointment slots for a clinic and specialty within a date range.
    date_range examples: 'next_7_days', 'next_14_days'.
    """
    slots = {
        ("Downtown Primary Care", "primary_care", "next_7_days"): [
            {"type": "telehealth", "start": "2026-01-15 10:30", "provider": "Dr. Kim"},
            {"type": "in_person", "start": "2026-01-16 16:00", "provider": "Dr. Kim"},
            {"type": "telehealth", "start": "2026-01-17 09:00", "provider": "NP Rivera"},
        ],
        ("Downtown Primary Care", "pulmonology", "next_14_days"): [
            {"type": "in_person", "start": "2026-01-22 11:00", "provider": "Dr. Chen"},
            {"type": "in_person", "start": "2026-01-28 14:30", "provider": "Dr. Chen"},
        ],
        ("Downtown Primary Care", "radiology", "next_7_days"): [
            {"type": "in_person", "start": "2026-01-16 09:00", "provider": "Imaging Center A"},
            {"type": "in_person", "start": "2026-01-19 14:00", "provider": "Imaging Center A"},
        ],
        ("Northside Pediatrics", "pediatrics", "next_7_days"): [
            {"type": "in_person", "start": "2026-01-15 15:00", "provider": "Dr. Owens"},
            {"type": "telehealth", "start": "2026-01-18 12:00", "provider": "Dr. Owens"},
        ],
    }

    key = (clinic, specialty, date_range)
    if key in slots:
        return json.dumps({"clinic": clinic, "specialty": specialty, "date_range": date_range, "slots": slots[key]}, indent=2)

    return json.dumps(
        {"clinic": clinic, "specialty": specialty, "date_range": date_range, "slots": [], "note": "No slots found for that combination."},
        indent=2,
    )
