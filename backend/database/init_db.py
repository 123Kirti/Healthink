import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "healthink.db")

conn = sqlite3.connect(DB_PATH)
conn.execute("PRAGMA foreign_keys = ON")

conn.execute("""
CREATE TABLE IF NOT EXISTS schemes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    details TEXT NOT NULL
)
""")

conn.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('patient', 'hospital', 'admin'))
)
""")

conn.execute("""
CREATE TABLE IF NOT EXISTS hospital_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    hospital_name TEXT NOT NULL,
    address TEXT,
    camp_details TEXT,
    created_at INTEGER NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
""")

conn.execute("""
CREATE TABLE IF NOT EXISTS patient_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    hospital_id INTEGER NOT NULL,
    scheme_id INTEGER,
    details TEXT NOT NULL,
    prescription_image TEXT,
    data_hash TEXT,
    timestamp INTEGER NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(hospital_id) REFERENCES hospital_profiles(id),
    FOREIGN KEY(scheme_id) REFERENCES schemes(id)
)
""")

existing_columns = [row[1] for row in conn.execute("PRAGMA table_info(patient_data)").fetchall()]

if "hospital_id" not in existing_columns:
    conn.execute("ALTER TABLE patient_data ADD COLUMN hospital_id INTEGER NOT NULL DEFAULT 1")

if "scheme_id" not in existing_columns:
    conn.execute("ALTER TABLE patient_data ADD COLUMN scheme_id INTEGER")

if "prescription_image" not in existing_columns:
    conn.execute("ALTER TABLE patient_data ADD COLUMN prescription_image TEXT")

if "data_hash" not in existing_columns:
    conn.execute("ALTER TABLE patient_data ADD COLUMN data_hash TEXT")

conn.commit()
conn.close()

print("Database initialized successfully")
