from flask import Flask, request, jsonify
from datetime import datetime
import os

app = Flask(__name__)

# ملاحظة: البيانات في القاموس ستتصفّر عند إعادة تشغيل السيرفر على Render
LICENSES = {
    "SR-TEST-001": {"expiry": "31-09-2026", "used_on": None},
    # "SR-TEST-003": {"expiry": "01-01-2027", "used_on": None},
    "SR-TEST-004": {"expiry": "04-04-2027", "used_on": None},
    "SR-TEST-005": {"expiry": "04-09-2026", "used_on": None},
}

@app.route('/')
def home():
    return "Server is running"

@app.route('/verify', methods=['POST'])
def verify():
    data = request.get_json() or {}
    serial = data.get('serial')
    device_id = data.get('device_id')

    if not serial or not device_id:
        return jsonify({"status": "missing_data", "message": "Serial or Device ID missing"}), 400

    if serial not in LICENSES: 
        return jsonify({"status": "invalid", "message": "License key not found"}), 404
        
    license_data = LICENSES[serial]
    expiry_date = datetime.strptime(license_data["expiry"], "%d-%m-%Y")
    
    if datetime.now() > expiry_date: 
        return jsonify({"status": "expired", "message": "License has expired"}), 403
        
    if license_data["used_on"] and license_data["used_on"] != device_id: 
        return jsonify({"status": "used", "message": "License already bound to another device"}), 403
        
    # تسجيل الجهاز إذا لم يكن مستخدماً
    if license_data["used_on"] is None: 
        LICENSES[serial]["used_on"] = device_id
        
    # إرجاع حالة النجاح مع تاريخ الانتهاء
    return jsonify({
        "status": "valid", 
        "expiry": license_data["expiry"],
        "message": "License verified successfully"
    }), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)