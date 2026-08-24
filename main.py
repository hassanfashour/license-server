from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# ========= قاعدة بيانات السيريالات =========
# الصيغة: "السريال": {"expiry": "يوم-شهر-سنة", "used_on": "ID الجهاز او None"}
LICENSES = {
    "SR-TEST-001": {"expiry": "31-12-2027", "used_on": None},
    "SR-DEMO-002": {"expiry": "31-12-2026", "used_on": None},
    # ضيف هون سيريالات جديدة
}
# =============================================

@app.route('/')
def home():
    return "License Server is Running"

@app.route('/activate', methods=['POST'])
def activate():
    try:
        data = request.json
        serial = data.get('serial')
        machine_id = data.get('machine_id')

        if not serial or not machine_id:
            return jsonify({"status": "error", "message": "بيانات ناقصة"}), 400

        if serial not in LICENSES:
            return jsonify({"status": "error", "message": "السريال غير صحيح"}), 400

        license = LICENSES[serial]

        # فحص التاريخ
        if datetime.now() > datetime.strptime(license["expiry"], "%d-%m-%Y"):
            return jsonify({"status": "error", "message": f"الترخيص منتهي بتاريخ {license['expiry']}"}), 400

        # فحص الجهاز
        if license["used_on"] is None:
            license["used_on"] = machine_id # اول تفعيل - نقفله على الجهاز
            print(f"تم تفعيل {serial} على جهاز {machine_id}")
            return jsonify({"status": "success", "message": "تم التفعيل بنجاح"})

        elif license["used_on"] == machine_id:
            return jsonify({"status": "success", "message": "الترخيص مفعل"}) # نفس الجهاز

        else:
            return jsonify({"status": "error", "message": "هذا السريال مستخدم على جهاز اخر"}), 400

    except Exception as e:
        return jsonify({"status": "error", "message": "خطأ في السيرفر"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)