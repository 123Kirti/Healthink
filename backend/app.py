from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import sqlite3
import os
import datetime
import hashlib
import json
from werkzeug.utils import secure_filename
from web3 import Web3

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "healthink.db")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

BLOCKCHAIN_RPC = os.environ.get("BLOCKCHAIN_RPC", "http://127.0.0.1:8545")
CONTRACT_ADDRESS = os.environ.get("CONTRACT_ADDRESS")
CONTRACT_ARTIFACT_PATH = os.path.join(BASE_DIR, "..", "blockchain", "build", "contracts", "HealthScheme.json")

w3 = None
contract = None
contract_owner = None

try:
    w3 = Web3(Web3.HTTPProvider(BLOCKCHAIN_RPC))
    if w3.is_connected():
        if CONTRACT_ADDRESS and os.path.exists(CONTRACT_ARTIFACT_PATH):
            with open(CONTRACT_ARTIFACT_PATH, "r") as contract_file:
                artifact = json.load(contract_file)
            contract = w3.eth.contract(address=w3.to_checksum_address(CONTRACT_ADDRESS), abi=artifact["abi"])
            try:
                accounts = w3.eth.accounts
            except Exception:
                accounts = w3.get_accounts() if hasattr(w3, "get_accounts") else []
            if accounts:
                contract_owner = accounts[0]
            else:
                contract_owner = os.environ.get("BLOCKCHAIN_OWNER")
    else:
        print("Blockchain provider not connected:", BLOCKCHAIN_RPC)
except Exception as e:
    print("Blockchain connection failed:", str(e))


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_database_schema():
    conn = get_db_connection()
    try:
        columns = [row["name"] for row in conn.execute("PRAGMA table_info(patient_data)").fetchall()]
        if "data_hash" not in columns:
            conn.execute("ALTER TABLE patient_data ADD COLUMN data_hash TEXT")
            conn.commit()
    except Exception:
        pass
    finally:
        conn.close()


ensure_database_schema()


def fetch_user(username):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    return dict(user) if user else None


def authenticate_user(username, password, role=None):
    user = fetch_user(username)
    if not user or user["password"] != password:
        return None
    if role and user["role"] != role:
        return None
    return user


def hash_record(details, hospital_id, scheme_id, prescription_image):
    composite = f"{details}|{hospital_id}|{scheme_id or ''}|{prescription_image or ''}"
    return hashlib.sha256(composite.encode("utf-8")).hexdigest()


def save_uploaded_file(uploaded_file):
    if not uploaded_file or uploaded_file.filename == "":
        return None
    filename = secure_filename(uploaded_file.filename)
    timestamp = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
    name, ext = os.path.splitext(filename)
    filename = f"{name}_{timestamp}{ext}"
    uploaded_file.save(os.path.join(UPLOAD_FOLDER, filename))
    return filename


def store_record_on_chain(record_hash, user_hash, record_type):
    if not contract or not w3 or not contract_owner:
        return None
    try:
        tx = contract.functions.storeRecord(bytes.fromhex(record_hash), bytes.fromhex(user_hash), record_type).transact({"from": contract_owner})
        receipt = w3.eth.wait_for_transaction_receipt(tx)
        return receipt.transactionHash.hex()
    except Exception as e:
        print("Blockchain record storage failed:", str(e))
        return None


@app.route("/")
def home():
    return jsonify({"message": "Healthink backend is running"})


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")
    role = data.get("role")

    if not username or not password or not role:
        return jsonify({"error": "Username, password and role are required"}), 400

    user = authenticate_user(username, password, role)
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    return jsonify({"username": user["username"], "role": user["role"]})


@app.route("/api/hospitals", methods=["GET"])
def get_hospitals():
    try:
        conn = get_db_connection()
        hospitals = conn.execute(
            "SELECT id, hospital_name, address FROM hospital_profiles ORDER BY hospital_name"
        ).fetchall()
        conn.close()
        return jsonify([
            {"id": row["id"], "name": row["hospital_name"], "address": row["address"]}
            for row in hospitals
        ])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/patient-data/submit", methods=["POST"])
def submit_patient_data():
    username = request.form.get("username")
    password = request.form.get("password")
    details = request.form.get("details")
    hospital_id = request.form.get("hospital_id")
    scheme_id = request.form.get("scheme_id")
    uploaded_image = request.files.get("prescription_image")

    if not username or not password or not details or not hospital_id:
        return jsonify({"error": "Username, password, hospital selection, and details are required."}), 400

    user = authenticate_user(username, password, "patient")
    if not user:
        return jsonify({"error": "Invalid patient credentials"}), 401

    if not hospital_id.isdigit():
        return jsonify({"error": "Hospital selection is invalid."}), 400

    hospital_id_value = int(hospital_id)
    scheme_id_value = int(scheme_id) if scheme_id and scheme_id.isdigit() else None
    image_filename = save_uploaded_file(uploaded_image)
    data_hash = hash_record(details, hospital_id_value, scheme_id_value, image_filename)

    try:
        conn = get_db_connection()
        hospital = conn.execute(
            "SELECT id FROM hospital_profiles WHERE id = ?",
            (hospital_id_value,)
        ).fetchone()
        if not hospital:
            conn.close()
            return jsonify({"error": "Selected hospital does not exist."}), 400

        conn.execute(
            "INSERT INTO patient_data (user_id, hospital_id, scheme_id, details, prescription_image, data_hash, timestamp) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                user["id"],
                hospital_id_value,
                scheme_id_value,
                details,
                image_filename,
                data_hash,
                int(datetime.datetime.utcnow().timestamp())
            )
        )
        conn.commit()
        record_id = conn.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]
        conn.close()

        blockchain_tx = None
        if contract:
            user_hash = hashlib.sha256(user["username"].encode("utf-8")).hexdigest()
            blockchain_tx = store_record_on_chain(data_hash, user_hash, "patient_record")

        return jsonify({
            "message": "Patient record submitted successfully",
            "record_id": record_id,
            "blockchain_transaction": blockchain_tx
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/patient-data", methods=["POST"])
def get_patient_data():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    user = authenticate_user(username, password, "patient")
    if not user:
        return jsonify({"error": "Invalid patient credentials"}), 401

    try:
        conn = get_db_connection()
        entries = conn.execute(
            "SELECT pd.id, pd.details, pd.timestamp, pd.prescription_image, pd.data_hash, "
            "hp.hospital_name AS hospital_name, s.name AS scheme_name "
            "FROM patient_data pd "
            "JOIN hospital_profiles hp ON pd.hospital_id = hp.id "
            "LEFT JOIN schemes s ON pd.scheme_id = s.id "
            "WHERE pd.user_id = ? ORDER BY pd.timestamp DESC",
            (user["id"],)
        ).fetchall()
        conn.close()

        result = [
            {
                "id": row["id"],
                "details": row["details"],
                "timestamp": row["timestamp"],
                "hospital": row["hospital_name"],
                "scheme": row["scheme_name"],
                "image_url": f"/api/uploads/{row['prescription_image']}" if row["prescription_image"] else None,
                "data_hash": row["data_hash"]
            }
            for row in entries
        ]
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/hospital-data", methods=["POST"])
def get_hospital_data():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    user = authenticate_user(username, password, "hospital")
    if not user:
        return jsonify({"error": "Invalid hospital credentials"}), 401

    try:
        conn = get_db_connection()
        hospital_profile = conn.execute(
            "SELECT id FROM hospital_profiles WHERE user_id = ?", (user["id"],)
        ).fetchone()
        if not hospital_profile:
            conn.close()
            return jsonify({"error": "Hospital profile not found"}), 404

        rows = conn.execute(
            "SELECT pd.id, u.username AS patient_username, pd.details, pd.timestamp, pd.prescription_image, s.name AS scheme_name "
            "FROM patient_data pd "
            "JOIN users u ON pd.user_id = u.id "
            "LEFT JOIN schemes s ON pd.scheme_id = s.id "
            "WHERE pd.hospital_id = ? ORDER BY pd.timestamp DESC",
            (hospital_profile["id"],)
        ).fetchall()
        conn.close()

        result = [
            {
                "id": row["id"],
                "patient": row["patient_username"],
                "details": row["details"],
                "scheme": row["scheme_name"],
                "timestamp": row["timestamp"],
                "image_url": f"/api/uploads/{row['prescription_image']}" if row["prescription_image"] else None
            }
            for row in rows
        ]
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/hospital-profile", methods=["POST"])
def get_hospital_profile():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    user = authenticate_user(username, password, "hospital")
    if not user:
        return jsonify({"error": "Invalid hospital credentials"}), 401

    try:
        conn = get_db_connection()
        profile = conn.execute(
            "SELECT hospital_name, address, camp_details FROM hospital_profiles WHERE user_id = ?",
            (user["id"],)
        ).fetchone()
        conn.close()

        if not profile:
            return jsonify({"error": "Hospital profile not found"}), 404

        return jsonify({
            "hospital_name": profile["hospital_name"],
            "address": profile["address"],
            "camp_details": profile["camp_details"]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/hospital-profile", methods=["PUT"])
def update_hospital_profile():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")
    hospital_name = data.get("hospital_name")
    address = data.get("address")
    camp_details = data.get("camp_details")

    if not username or not password or not hospital_name or not address:
        return jsonify({"error": "Username, password, hospital name and address are required"}), 400

    user = authenticate_user(username, password, "hospital")
    if not user:
        return jsonify({"error": "Invalid hospital credentials"}), 401

    try:
        conn = get_db_connection()
        profile = conn.execute(
            "SELECT id FROM hospital_profiles WHERE user_id = ?",
            (user["id"],)
        ).fetchone()

        if profile:
            conn.execute(
                "UPDATE hospital_profiles SET hospital_name = ?, address = ?, camp_details = ? WHERE user_id = ?",
                (hospital_name, address, camp_details, user["id"])
            )
        else:
            conn.execute(
                "INSERT INTO hospital_profiles (user_id, hospital_name, address, camp_details, created_at) VALUES (?, ?, ?, ?, ?)",
                (user["id"], hospital_name, address, camp_details, int(datetime.datetime.utcnow().timestamp()))
            )

        conn.commit()
        conn.close()
        return jsonify({"message": "Hospital profile updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/admin/records", methods=["POST"])
def get_admin_records():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    user = authenticate_user(username, password, "admin")
    if not user:
        return jsonify({"error": "Invalid admin credentials"}), 401

    try:
        conn = get_db_connection()
        rows = conn.execute(
            "SELECT pd.id, u.username AS patient_username, hp.hospital_name, s.name AS scheme_name, pd.timestamp, pd.data_hash "
            "FROM patient_data pd "
            "JOIN users u ON pd.user_id = u.id "
            "JOIN hospital_profiles hp ON pd.hospital_id = hp.id "
            "LEFT JOIN schemes s ON pd.scheme_id = s.id "
            "ORDER BY pd.timestamp DESC"
        ).fetchall()
        conn.close()

        result = [
            {
                "id": row["id"],
                "patient": row["patient_username"],
                "hospital": row["hospital_name"],
                "scheme": row["scheme_name"],
                "timestamp": row["timestamp"],
                "record_hash": row["data_hash"]
            }
            for row in rows
        ]
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.route("/api/schemes", methods=["GET"])
def get_schemes():
    try:
        conn = get_db_connection()
        schemes = conn.execute("SELECT * FROM schemes").fetchall()
        conn.close()
        return jsonify([dict(row) for row in schemes])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/schemes/<int:scheme_id>", methods=["GET"])
def get_scheme(scheme_id):
    try:
        conn = get_db_connection()
        scheme = conn.execute("SELECT * FROM schemes WHERE id = ?", (scheme_id,)).fetchone()
        conn.close()
        if scheme:
            return jsonify(dict(scheme))
        else:
            return jsonify({"error": "Scheme not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy"})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
