from flask import Flask, render_template, request, jsonify
import subprocess

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run_python', methods=['POST'])
def run_python():
    file = request.files['file']
    if file:
        filepath = f'temp_{file.filename}'
        file.save(filepath)
        try:
            result = subprocess.check_output(
                ['python', filepath],
                stderr=subprocess.STDOUT,
                timeout=10,
                text=True
            )
        except subprocess.CalledProcessError as e:
            result = e.output
        except subprocess.TimeoutExpired:
            result = "⏱️ العملية تجاوزت الوقت المسموح به."
        return jsonify({'output': result})
    return jsonify({'output': '❌ لم يتم رفع أي ملف.'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)