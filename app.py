from flask import Flask, render_template, request, redirect, url_for, flash
import os
import json

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Setzt einen zufälligen geheimen Schlüssel

# Konfiguration
UPLOAD_FOLDER = "data"
DATA_FILE = "data.json"
STATIC_FOLDER = "static/images"

# Falls Ordner nicht existieren, erstelle sie
for folder in [UPLOAD_FOLDER, STATIC_FOLDER]:
    os.makedirs(folder, exist_ok=True)

# Daten laden und speichern
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
        try:
            os.remove(os.path.join(UPLOAD_FOLDER, file_to_delete))
            data.remove(file_to_delete)
            save_data(data)
            flash(f"Datei '{file_to_delete}' wurde gelöscht.")
        except Exception as e:
            flash(f"Fehler beim Löschen: {e}")

    return redirect(url_for('cloud'))

# Starte Flask für externe Verbindungen
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
