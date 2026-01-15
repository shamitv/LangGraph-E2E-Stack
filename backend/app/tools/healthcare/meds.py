import json
from langchain_core.tools import tool

@tool("medication_info")
def medication_info(drug: str) -> str:
    """
    Return high-level medication info (class, common use, notes).
    """
    db = {
        "albuterol": {
            "class": "short-acting bronchodilator",
            "common_use": "relief of acute asthma symptoms (rescue inhaler)",
            "notes": ["Often requires periodic clinician review for refill policies.", "Check interaction/allergy history."],
        },
        "amoxicillin": {
            "class": "antibiotic (penicillin family)",
            "common_use": "bacterial infections (requires clinician evaluation)",
            "notes": ["Contraindicated if penicillin allergy is present.", "Typically not prescribed without appropriate evaluation."],
        },
        "oxycodone": {
            "class": "opioid analgesic (controlled substance)",
            "common_use": "moderate-to-severe pain (strict policy controls)",
            "notes": ["Controlled substance: additional safeguards and in-person requirements may apply."],
        },
    }
    k = drug.strip().lower()
    if k in db:
        return json.dumps({"item": drug, **db[k]}, indent=2)
    return json.dumps({"item": drug, "note": "Not found in mock medication database."}, indent=2)
