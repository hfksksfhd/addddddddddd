from flask import Flask, request, render_template
import subprocess

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/run', methods=['POST'])
def run():
    code = request.form['code']
    with open("user_code.py", "w", encoding="utf-8") as f:
        f.write(code)
    try:
        result = subprocess.run(
            ['python', 'user_code.py'],
            capture_output=True,
            text=True,
            timeout=30
        )
        output = result.stdout + result.stderr
    except Exception as e:
        output = str(e)
    return render_template('index.html', output=output, code=code)

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
