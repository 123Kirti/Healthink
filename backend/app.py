from flask import Flask, jsonify
import sqlite3

app = Flask(__name__)
DB_PATH = "backend/database/healthink.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def home():
    return "Healthink backend is running"

@app.route("/api/schemes", methods=["GET"])
def get_schemes():
    conn = get_db_connection()
    schemes = conn.execute("SELECT * FROM schemes").fetchall()
    conn.close()
    return jsonify([dict(row) for row in schemes])

if __name__ == "__main__":
    app.run(debug=True)
