from flask import Flask, request, jsonify
from datetime import datetime
import os

app = Flask(__name__) # <-- هذا اهم سطر

LICENSES = {
    "SR-TEST-001": {"expiry": "31-12-2027", "used_on": None},
}

@app.route('/')
def home():
    return "Server is running"

@app.route('/verify', methods=['POST'])
def verify():
    data = request.get_json()
    serial = data.get('serial')
    device_id = data.get('device_id')
    if serial not in LICENSES: return jsonify({"status": "invalid"}), 404
    license_data = LICENSES[serial]
    expiry_date = datetime.strptime(license_data["expiry"], "%d-%m-%Y")
    if datetime.now() > expiry_date: return jsonify({"status": "expired"}), 403
    if license_data["used_on"] and license_data["used_on"]!= device_id: return jsonify({"status": "used"}), 403
    if license_data["used_on"] is None: LICENSES[serial]["used_on"] = device_id
    return jsonify({"status": "valid"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)