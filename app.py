from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

@app.route('/install_library', methods=['POST'])
def install_library():
    data = request.get_json()
    lib = data.get('library')

    if not lib:
        return jsonify({"message": "لم يتم تحديد اسم المكتبة."}), 400

    try:
        # تشغيل pip install
        result = subprocess.run(
            ['pip', 'install', lib],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode == 0:
            return jsonify({"message": f"تم تثبيت المكتبة بنجاح:\n{result.stdout}"})
        else:
            return jsonify({"message": f"حدث خطأ أثناء التثبيت:\n{result.stderr}"}), 500
    except Exception as e:
        return jsonify({"message": f"خطأ غير متوقع: {str(e)}"}), 500

# باقي كود flask موجود هنا...

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
