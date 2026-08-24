from flask import Flask, request, jsonify
from datetime import datetime
import os

app = Flask(__name__)

# ====== قاعدة بيانات السيريالات ======
# تقدر تضيف براحتك هون
LICENSES = {
    "SR-TEST-001": {"expiry": "31-12-2027", "used_on": None},
    "SR-DEMO-002": {"expiry": "31-12-2026", "used_on": None},
    "SR-PRO-003": {"expiry": "31-12-2025", "used_on": None},
}

# ====== الصفحات ======

@app.route('/')
def home():
    return "Server is running"

@app.route('/verify', methods=['POST'])
def verify():
    data = request.get_json()

    if not data:
        return jsonify({"status": "error", "message": "No data sent"}), 400

    serial = data.get('serial')
    device_id = data.get('device_id')

    if not serial or not device_id:
        return jsonify({"status": "error", "message": "serial and device_id required"}), 400

    if serial not in LICENSES:
        return jsonify({"status": "invalid", "message": "Serial not found"}), 404

    license_data = LICENSES[serial]

    # 1. فحص الانتهاء
    expiry_date = datetime.strptime(license_data["expiry"], "%d-%m-%Y")
    if datetime.now() > expiry_date:
        return jsonify({"status": "expired", "message": "License expired"}), 403

    # 2. فحص الاستخدام على جهاز ثاني
    if license_data["used_on"] is not None and license_data["used_on"]!= device_id:
        return jsonify({"status": "used", "message": "License already used on another device"}), 403

    # 3. لو اول مرة: سجل الجهاز
    if license_data["used_on"] is None:
        LICENSES[serial]["used_on"] = device_id

    return jsonify({"status": "valid", "message": "License is valid"}), 200

# ====== مهم عشان Render ======
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)