import sqlite3

conn = sqlite3.connect("healthink.db")

conn.execute("""
CREATE TABLE IF NOT EXISTS schemes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    details TEXT NOT NULL
)
""")

conn.commit()
conn.close()

print("Database initialized successfully")
