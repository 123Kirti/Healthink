import sqlite3

conn = sqlite3.connect("healthink.db")

schemes = [
    ("Ayushman Bharat", "Health insurance up to 5 lakh for poor families"),
    ("Jan Aushadhi", "Affordable medicines through government stores"),
    ("Rashtriya Swasthya Bima Yojana", "Health coverage for unorganized workers")
]

for scheme in schemes:
    conn.execute(
        "INSERT OR IGNORE INTO schemes (name, details) VALUES (?, ?)",
        scheme
    )

conn.commit()
conn.close()

print("Schemes inserted successfully")
