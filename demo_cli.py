"""
demo_cli.py
Interactive simulator for testing the prototype before building the UI.
"""
from agent_router import handle_patient_request
from pioneer_mock_db import init_mock_pioneer_db

if __name__ == "__main__":
    init_mock_pioneer_db()
    test_phone = "5550199"

    print("\n--- PHARMACY PILOT DEMO (Patient: John Doe | 555-0199) ---")
    
    test_prompts = [
        "What prescriptions do I have on file?",
        "Can I get a refill on my Lisinopril?",
        "Can you refill my Metformin please?",
        "I need more Adderall."
    ]

    for p in test_prompts:
        print(f"\n[Patient SMS]: {p}")
        response = handle_patient_request(test_phone, p)
        print(f"[Pilot AI]:\n{response}")
