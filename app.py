from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
import os
import json

app = Flask(__name__)
app.secret_key = os.urandom(24)

UPLOAD_FOLDER = "data"
STATIC_FOLDER = "static/images"
DATA_FILE = "data.json"

for folder in [UPLOAD_FOLDER, STATIC_FOLDER]:
    os.makedirs(folder, exist_ok=True)

def load_data():
    return json.load(open(DATA_FILE, "r", encoding="utf-8")) if os.path.exists(DATA_FILE) else []

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

@app.route('/')
def cloud():
    return render_template('cloud.html', files=load_data())

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files.get('file')
    if file and file.filename:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)
        data = load_data()
        if file.filename not in data:
            data.append(file.filename)
            save_data(data)
        flash(f"Datei '{file.filename}' hochgeladen.")
    return redirect(url_for('cloud'))

@app.route('/delete', methods=['POST'])
def delete_file():
    file_to_delete = request.form['file_to_delete']
    data = load_data()
    if file_to_delete in data:
        os.remove(os.path.join(UPLOAD_FOLDER, file_to_delete))
        data.remove(file_to_delete)
        save_data(data)
        flash(f"Datei '{file_to_delete}' wurde gelöscht.")
    return redirect(url_for('cloud'))

@app.route('/data/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
