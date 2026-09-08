"""
pharmacy_tools.py
Deterministic business rules that query and update the mock PioneerRx database.
"""
import sqlite3
from datetime import datetime

DB_PATH = "pioneer_mock.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def verify_patient_by_phone(phone: str):
    conn = get_db()
    cur = conn.cursor()
    clean_phone = "".join(filter(str.isdigit, phone))
    cur.execute("SELECT * FROM patients WHERE phone_number = ?", (clean_phone,))
    patient = cur.fetchone()
    conn.close()
    return dict(patient) if patient else None

def get_patient_active_meds(patient_id: int):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT rx_number, drug_name, dosage, refills_remaining, is_controlled, expiration_date
        FROM prescriptions 
        WHERE patient_id = ? AND status = 'ACTIVE'
    """, (patient_id,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def request_refill(rx_number: str, patient_id: int) -> dict:
    conn = get_db()
    cur = conn.cursor()

    # Step 1: Validate Prescription Status
    cur.execute("SELECT * FROM prescriptions WHERE rx_number = ? AND patient_id = ?", (rx_number, patient_id))
    rx = cur.fetchone()

    if not rx:
        conn.close()
        return {"success": False, "reason": "PRESCRIPTION_NOT_FOUND", "message": "Prescription record could not be located."}

    # Step 2: Clinical & Regulatory Safety Checks
    if rx["is_controlled"] == 1:
        conn.close()
        return {
            "success": False,
            "reason": "CONTROLLED_SUBSTANCE",
            "message": f"{rx['drug_name']} is a controlled medication and requires direct pharmacist/provider authorization."
        }

    if rx["refills_remaining"] <= 0:
        conn.close()
        return {
            "success": False,
            "reason": "NO_REFILLS_LEFT",
            "message": f"You have 0 refills left on {rx['drug_name']}. Would you like us to contact your prescriber for a renewal?"
        }

    # Step 3: Enqueue in PioneerRx
    cur.execute("""
        INSERT INTO refill_queue (rx_number, source, status, notes)
        VALUES (?, 'AI_PATIENT_COPILOT', 'QUEUED_FOR_FILL', ?)
    """, (rx_number, f"Refill requested for {rx['drug_name']} {rx['dosage']}"))

    # Decrement remaining count
    cur.execute("UPDATE prescriptions SET refills_remaining = refills_remaining - 1 WHERE rx_number = ?", (rx_number,))

    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": f"Refill confirmed for {rx['drug_name']} {rx['dosage']}. It has been placed in the pharmacy queue for pickup today."
    }
