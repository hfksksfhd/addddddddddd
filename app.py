from flask import Flask, request, render_template
import subprocess
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/run', methods=['POST'])
def run():
    uploaded_file = request.files['file']
    if uploaded_file.filename.endswith('.py'):
        filepath = os.path.join(UPLOAD_FOLDER, uploaded_file.filename)
        uploaded_file.save(filepath)
        try:
            result = subprocess.run(
                ['python', filepath],
                capture_output=True,
                text=True,
                timeout=30
            )
            output = result.stdout + result.stderr
        except Exception as e:
            output = str(e)
    else:
        output = "الملف غير صالح. فقط ملفات .py مدعومة."
    return render_template('index.html', output=output)

@app.route('/install', methods=['POST'])
def install():
    package = request.form['package']
    try:
        result = subprocess.run(
            ['pip', 'install', package],
            capture_output=True,
            text=True,
            timeout=30
        )
        output = result.stdout + result.stderr
    except Exception as e:
        output = str(e)
    return render_template('index.html', install_output=output)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
