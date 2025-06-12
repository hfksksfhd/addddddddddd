from flask import Flask, request, jsonify, session, render_template
import subprocess
import os
import uuid
import shutil

app = Flask(__name__)
app.secret_key = 'سر-سري-جداً-لتشفير-الجلسات'

BASE_VENV_DIR = '/tmp/user_venvs'  # مكان حفظ بيئات المستخدمين المؤقتة
os.makedirs(BASE_VENV_DIR, exist_ok=True)

def get_user_id():
    if 'user_id' not in session:
        session['user_id'] = uuid.uuid4().int >> 64  # رقم فريد لكل جلسة
    return session['user_id']

def get_scope(user_id):
    # تقسيم المستخدمين لمجموعات كل 5 مستخدمين نطاق
    return (user_id % 1000000) // 5 + 1

def get_venv_path(user_id):
    return os.path.join(BASE_VENV_DIR, f'venv_{user_id}')

def ensure_venv(user_id):
    venv_path = get_venv_path(user_id)
    if not os.path.exists(venv_path):
        # إنشاء بيئة افتراضية
        subprocess.run(['python3', '-m', 'venv', venv_path])
    return venv_path

@app.route('/')
def index():
    user_id = get_user_id()
    scope = get_scope(user_id)
    return render_template('index.html', scope=scope)

@app.route('/install_library', methods=['POST'])
def install_library():
    user_id = get_user_id()
    data = request.get_json()
    lib = data.get('library')
    if not lib:
        return jsonify({"message": "لم يتم تحديد اسم المكتبة."}), 400

    # تثبيت المكتبة في بيئة المستخدم الافتراضية
    venv_path = ensure_venv(user_id)
    pip_path = os.path.join(venv_path, 'bin', 'pip')
    result = subprocess.run([pip_path, 'install', lib], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if result.returncode == 0:
        return jsonify({"message": f"تم تثبيت المكتبة '{lib}' بنجاح."})
    else:
        return jsonify({"message": f"خطأ في تثبيت المكتبة '{lib}':\n{result.stderr}"}), 500

@app.route('/run_python', methods=['POST'])
def run_python():
    user_id = get_user_id()

    if 'file' not in request.files:
        return jsonify({"output": "لم يتم إرسال ملف."}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"output": "الرجاء اختيار ملف بايثون."}), 400

    code_path = f'/tmp/code_{user_id}.py'
    file.save(code_path)

    venv_path = ensure_venv(user_id)
    python_path = os.path.join(venv_path, 'bin', 'python')

    try:
        proc = subprocess.run([python_path, code_path],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              timeout=1000, text=True)
        output = proc.stdout + proc.stderr
    except subprocess.TimeoutExpired:
        output = "انتهى الوقت المحدد لتنفيذ البرنامج."

    # حذف ملف الكود بعد التشغيل
    os.remove(code_path)

    return jsonify({"output": output})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
