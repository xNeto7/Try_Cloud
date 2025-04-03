from flask import Flask, render_template, request, send_from_directory, redirect, url_for, flash
import os
import subprocess
import json

app = Flask(__name__)

# Geheimschlüssel für Flash-Nachrichten
app.secret_key = 'renas'

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
        flash("Keine Datei ausgewählt.")
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        flash("Keine Datei ausgewählt.")
        return redirect(request.url)
    
    # Speichern der Datei im Datenordner
    file_path = os.path.join(DATA_FOLDER, file.filename)
    file.save(file_path)
    
    # Daten aktualisieren und speichern
    data = load_data()
    data.append(file.filename)
    save_data(data)

    # Git-Upload (optional)
    try:
        subprocess.run(["git", "add", DATA_FOLDER], check=True)
        subprocess.run(["git", "commit", "-m", "update data"], check=True)
        subprocess.run(["git", "push"], check=True)
        flash("Datei erfolgreich hochgeladen und auf GitHub gepusht.")
    except subprocess.CalledProcessError as e:
        flash(f"Fehler beim Hochladen der Datei auf GitHub: {e}")
    
    return redirect(url_for('cloud'))

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(DATA_FOLDER, filename)

@app.route('/delete', methods=['POST'])
def delete_file():
    file_to_delete = request.form['file_to_delete']
    data = load_data()
    
    if file_to_delete in data:
        file_path = os.path.join(DATA_FOLDER, file_to_delete)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                data = [f for f in data if f != file_to_delete]
                save_data(data)
                flash(f"Datei '{file_to_delete}' wurde erfolgreich gelöscht.")
            except Exception as e:
                flash(f"Fehler beim Löschen der Datei: {e}")
        else:
            flash(f"Fehler: Datei '{file_to_delete}' existiert nicht im Verzeichnis.")
    else:
        flash(f"Fehler: Datei '{file_to_delete}' wurde nicht in der Datenliste gefunden.")
    
    return redirect(url_for('cloud'))

if __name__ == '__main__':
    app.run(debug=True)
