from flask import Flask, render_template, request, send_from_directory, redirect, url_for
import os
import shutil
import json
import subprocess

app = Flask(__name__)

DATA_FOLDER = "data"
DATA_FILE = "data.json"

if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return []

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

@app.route('/')
def cloud():
    files = load_data()
    return render_template('cloud.html', files=files)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    
    # Speichern der Datei im Datenordner
    file_path = os.path.join(DATA_FOLDER, file.filename)
    file.save(file_path)
    
    # Daten aktualisieren und speichern
    data = load_data()
    data.append(file.filename)
    save_data(data)

    # Git-Upload (optional)
    subprocess.run(["git", "add", DATA_FOLDER], check=True)
    subprocess.run(["git", "commit", "-m", "update data"], check=True)
    subprocess.run(["git", "push"], check=True)

    return redirect(url_for('index'))

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(DATA_FOLDER, filename)

@app.route('/delete', methods=['POST'])
def delete_file():
    file_to_delete = request.form['file_to_delete']
    data = load_data()
    
    # Überprüfen, ob die Datei existiert
    if file_to_delete in data:
        # Datei löschen
        file_path = os.path.join(DATA_FOLDER, file_to_delete)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Dateiliste aktualisieren
        data.remove(file_to_delete)
        save_data(data)

        # Git-Update
        subprocess.run(["git", "add", DATA_FOLDER], check=True)
        subprocess.run(["git", "commit", "-m", "delete data"], check=True)
        subprocess.run(["git", "push"], check=True)
    
    return redirect(url_for('cloud'))

if __name__ == '__main__':
    app.run(debug=True)
