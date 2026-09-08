"""
pioneer_mock_db.py
Creates a local SQLite database that mirrors a realistic PioneerRx schema.
"""
import sqlite3
from datetime import date, timedelta

def init_mock_pioneer_db(db_path="pioneer_mock.db"):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # 1. Patients Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        phone_number TEXT UNIQUE NOT NULL,
        dob TEXT NOT NULL
    );
    """)

    # 2. Prescriptions Table (Rx Profile)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS prescriptions (
        rx_number TEXT PRIMARY KEY,
        patient_id INTEGER NOT NULL,
        drug_name TEXT NOT NULL,
        dosage TEXT NOT NULL,
        refills_remaining INTEGER NOT NULL,
        is_controlled BOOLEAN NOT NULL DEFAULT 0,
        expiration_date TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'ACTIVE',
        FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
    );
    """)

    # 3. Refill Queue (Where Pioneer queues orders for technician review)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS refill_queue (
        queue_id INTEGER PRIMARY KEY AUTOINCREMENT,
        rx_number TEXT NOT NULL,
        requested_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        source TEXT DEFAULT 'AI_PATIENT_COPILOT',
        status TEXT DEFAULT 'PENDING_FILL',
        notes TEXT
    );
    """)

    # Seed initial test data
    cur.execute("DELETE FROM patients")
    cur.execute("DELETE FROM prescriptions")
    cur.execute("DELETE FROM refill_queue")

    # Sample patient: John Doe (Phone: 555-0199)
    cur.execute("""
    INSERT INTO patients (first_name, last_name, phone_number, dob)
    VALUES ('John', 'Doe', '5550199', '1985-04-12')
    """)
    patient_id = cur.lastrowid

    # Active refill available
    cur.execute("""
    INSERT INTO prescriptions VALUES 
    ('RX-100201', ?, 'Lisinopril', '10mg Tablet', 3, 0, ?, 'ACTIVE')
    """, (patient_id, (date.today() + timedelta(days=180)).isoformat()))

    # 0 refills remaining (needs doctor authorization)
    cur.execute("""
    INSERT INTO prescriptions VALUES 
    ('RX-100202', ?, 'Metformin', '500mg ER', 0, 0, ?, 'ACTIVE')
    """, (patient_id, (date.today() + timedelta(days=90)).isoformat()))

    # Controlled substance (Schedule II - cannot be auto-refilled)
    cur.execute("""
    INSERT INTO prescriptions VALUES 
    ('RX-100203', ?, 'Adderall', '20mg XR', 1, 1, ?, 'ACTIVE')
    """, (patient_id, (date.today() + timedelta(days=30)).isoformat()))

    conn.commit()
    conn.close()
    print("Mock PioneerRx database initialized successfully as 'pioneer_mock.db'.")

if __name__ == "__main__":
    init_mock_pioneer_db()
