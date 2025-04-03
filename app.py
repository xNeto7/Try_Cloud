from flask import Flask, render_template, request, redirect, url_for, flash
import os
import json
import subprocess

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Setzt einen zufälligen geheimen Schlüssel

# Konfiguration
DATA_FOLDER = "data"
DATA_FILE = "data.json"
GITHUB_REPO_URL = "https://github.com/xNeto7/Try_Cloud/raw/main/data/"

# Wenn der Ordner nicht existiert, erstelle ihn
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

# Laden und Speichern der Daten
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

    return redirect(url_for('cloud'))

@app.route('/download/<filename>')
def download_file(filename):
    # Erstelle die GitHub-URL zum direkten Download der Datei
    github_file_url = GITHUB_REPO_URL + filename
    return redirect(github_file_url)

@app.route('/delete', methods=['POST'])
def delete_file():
    file_to_delete = request.form['file_to_delete']
    data = load_data()

    if file_to_delete in data:
        print(f"Versuche, Datei '{file_to_delete}' von GitHub zu löschen...")  # Debug-Ausgabe

        try:
            # GitHub-Datei entfernen
            subprocess.run(["git", "rm", os.path.join(DATA_FOLDER, file_to_delete)], check=True)
            subprocess.run(["git", "commit", "-m", f"Remove file {file_to_delete}"], check=True)
            subprocess.run(["git", "push"], check=True)
            print(f"Datei '{file_to_delete}' erfolgreich von GitHub gelöscht.")  # Debug-Ausgabe
            
            # Entfernen der Datei aus der JSON-Datenstruktur
            data = [f for f in data if f != file_to_delete]
            save_data(data)
            flash(f"Datei '{file_to_delete}' wurde erfolgreich gelöscht.")
        except Exception as e:
            print(f"Fehler beim Löschen der Datei von GitHub: {e}")
            flash(f"Fehler beim Löschen der Datei: {e}")
    else:
        flash(f"Fehler: Datei '{file_to_delete}' wurde nicht in der Datenliste gefunden.")
    
    # Lade die aktualisierten Daten nach dem Löschen
    files = load_data()
    return render_template('cloud.html', files=files)  # Gibt die aktualisierte Ansicht zurück

# Wenn dies das Hauptmodul ist, starte den Server
if __name__ == '__main__':
    # Flask so konfigurieren, dass es auf allen IP-Adressen (0.0.0.0) und Port 5000 läuft
    app.run(debug=True, host='0.0.0.0', port=5000)
