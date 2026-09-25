from flask import Flask, request, jsonify
from datetime import datetime
import os

app = Flask(__name__)

# ملاحظة: البيانات في القاموس ستتصفّر عند إعادة تشغيل السيرفر على Render
LICENSES = {
    "7YGPK-KULE5-FWZDY-5CUDP": {"expiry": "22-10-2026", "used_on": None}, #Hassan
    "5GP2R-SW4GR-AGN9F-KCBGN": {"expiry": "01-10-2026", "used_on": None}, #HBF
    "3ZHP8-4CMGH-HEL4L-7J9HN": {"expiry": "27-09-2026", "used_on": None}, #ISLAM
    "TVYNH-JPFJ7-29TL4-PTFKQ": {"expiry": "02-10-2026", "used_on": None}, #SaYa
    "R8FSU-AV4SB-9EUXQ-6GRMP": {"expiry": "25-10-2026", "used_on": None}, #OMER
    # "SR-TEST-005": {"expiry": "01-09-2026", "used_on": None},
    # "SR-TEST-006": {"expiry": "17-09-2027", "used_on": None},
    # "SR-TEST-007": {"expiry": "14-09-2026", "used_on": None},
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
