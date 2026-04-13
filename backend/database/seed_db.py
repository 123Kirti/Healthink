import hashlib
import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "healthink.db")
conn = sqlite3.connect(DB_PATH)
conn.execute("PRAGMA foreign_keys = ON")

schemes = [
    ("Ayushman Bharat", "Health insurance up to 5 lakh for poor families"),
    ("Jan Aushadhi", "Affordable medicines through government stores"),
    ("Rashtriya Swasthya Bima Yojana", "Health coverage for unorganized workers")
]

users = [
    ("patient1", "patient123", "patient"),
    ("hospital1", "hospital123", "hospital"),
    ("admin1", "admin123", "admin")
]

for scheme in schemes:
    conn.execute(
        "INSERT OR IGNORE INTO schemes (name, details) VALUES (?, ?)",
        scheme
    )

for user in users:
    conn.execute(
        "INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)",
        user
    )

conn.execute(
    "INSERT OR IGNORE INTO hospital_profiles (user_id, hospital_name, address, camp_details, created_at) "
    "VALUES ((SELECT id FROM users WHERE username = ?), ?, ?, ?, strftime('%s','now'))",
    ("hospital1", "Healthink Hospital", "123 Health St, City", "Community health camps under government schemes")
)

patient_hash = hashlib.sha256("patient1|1|1|Initial check-up record|sample-prescription.png".encode()).hexdigest()
conn.execute(
    "INSERT INTO patient_data (user_id, hospital_id, scheme_id, details, prescription_image, data_hash, timestamp) "
    "VALUES ((SELECT id FROM users WHERE username = ?), (SELECT id FROM hospital_profiles WHERE user_id = (SELECT id FROM users WHERE username = ?)), ?, ?, ?, ?, strftime('%s','now'))",
    ("patient1", "hospital1", 1, "Routine health check-up and prescription uploaded.", "sample-prescription.png", patient_hash)
)

conn.commit()
conn.close()

print("Sample data inserted successfully")
