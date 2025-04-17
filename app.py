from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import os
import json
import subprocess

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Setzt einen zufälligen geheimen Schlüssel

# Konfiguration
DATA_FOLDER = "data"
DATA_FILE = "data.json"
USERS_FILE = "users.json"
GITHUB_REPO_URL = "https://github.com/xNeto7/Try_Cloud/raw/main/data/"

# Wenn der Ordner nicht existiert, erstelle ihn
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

# Nutzer laden/speichern

def lade_nutzer():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

def speichere_nutzer(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

# Daten laden/speichern

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return []

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

# Authentifizierung

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = lade_nutzer()

        if username in users:
            flash("Benutzername existiert bereits.")
            return redirect(url_for('register'))

        users[username] = password
        speichere_nutzer(users)
        flash("Registrierung erfolgreich. Bitte einloggen.")
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = lade_nutzer()

        if username in users and users[username] == password:
            session['username'] = username
            flash("Login erfolgreich!")
            return redirect(url_for('cloud'))
        else:
            flash("Login fehlgeschlagen.")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("Abgemeldet.")
    return redirect(url_for('login'))

@app.route('/download/<filename>')
def download_file(filename):
    github_file_url = GITHUB_REPO_URL + filename
    return redirect(github_file_url)

@app.route('/files')
def get_files():
    files = load_data()
    return jsonify(files)

@app.route('/')
def cloud():
    if 'username' not in session:
        return redirect(url_for('login'))
    files = load_data()
    return render_template('cloud.html', files=files)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)

    file_path = os.path.join(DATA_FOLDER, file.filename)
    file.save(file_path)

    data = load_data()
    data.append(file.filename)
    save_data(data)

    subprocess.run(["git", "add", DATA_FOLDER], check=True)
    subprocess.run(["git", "commit", "-m", "update data"], check=True)
    subprocess.run(["git", "push"], check=True)

    return redirect(url_for('cloud'))

@app.route('/delete', methods=['POST'])
def delete_file():
    file_to_delete = request.form['file_to_delete']
    data = load_data()

    if file_to_delete in data:
        try:
            subprocess.run(["git", "rm", os.path.join(DATA_FOLDER, file_to_delete)], check=True)
            subprocess.run(["git", "commit", "-m", f"Remove file {file_to_delete}"], check=True)
            subprocess.run(["git", "push"], check=True)

            data = [f for f in data if f != file_to_delete]
            save_data(data)
            flash(f"Datei '{file_to_delete}' wurde erfolgreich gelöscht.")
        except Exception as e:
            flash(f"Fehler beim Löschen der Datei: {e}")
    else:
        flash(f"Fehler: Datei '{file_to_delete}' wurde nicht gefunden.")

    files = load_data()
    return render_template('cloud.html', files=files)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)