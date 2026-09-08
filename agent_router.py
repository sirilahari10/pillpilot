"""
agent_router.py
Lightweight dispatcher mapping patient natural language to pharmacy operations.
"""
from pharmacy_tools import verify_patient_by_phone, get_patient_active_meds, request_refill

def handle_patient_request(phone_number: str, message: str) -> str:
    # 1. Look up patient identity by incoming phone number
    patient = verify_patient_by_phone(phone_number)
    if not patient:
        return "We could not locate a pharmacy profile matching this phone number. Please call the pharmacy directly to register."

    text = message.lower()
    meds = get_patient_active_meds(patient["patient_id"])

    # 2. Intent: Check Status / List Meds
    if any(k in text for k in ["what meds", "list", "my prescriptions", "status"]):
        if not meds:
            return f"Hello {patient['first_name']}, you have no active prescriptions on file."
        
        summary = [f"• {m['drug_name']} ({m['dosage']}) - {m['refills_remaining']} refills remaining" for m in meds]
        return f"Hello {patient['first_name']}, here are your current prescriptions:\n" + "\n".join(summary)

    # 3. Intent: Refill Request
    if any(k in text for k in ["refill", "fill", "renew", "need more"]):
        # Match target drug name against the patient's active profile
        matched_rx = None
        for med in meds:
            if med["drug_name"].lower() in text:
                matched_rx = med
                break

        if not matched_rx:
            drug_names = ", ".join([m["drug_name"] for m in meds])
            return f"Which medication would you like to refill? Your active profile includes: {drug_names}."

        result = request_refill(matched_rx["rx_number"], patient["patient_id"])
        return result["message"]

    # 4. Fallback / Triage
    return f"Hi {patient['first_name']}, I can help you check your active medications or request a refill. What would you like to do?"
