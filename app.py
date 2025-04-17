from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import os
import json
import subprocess

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Konfiguration
DATA_FOLDER = "data"
USERS_FILE = "users.json"
GITHUB_REPO_URL = "https://github.com/xNeto7/Try_Cloud/raw/main/data/"

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

def get_user_folder(username):
    folder = os.path.join(DATA_FOLDER, username)
    if not os.path.exists(folder):
        os.makedirs(folder)
    return folder

def get_user_data_file(username):
    return os.path.join(get_user_folder(username), "data.json")

def load_data(username):
    data_file = get_user_data_file(username)
    if os.path.exists(data_file):
        with open(data_file, "r", encoding="utf-8") as file:
            return json.load(file)
    return []

def save_data(username, data):
    data_file = get_user_data_file(username)
    with open(data_file, "w", encoding="utf-8") as file:
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

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    flash("Abgemeldet.")
    return redirect(url_for('login'))


@app.route('/download/<filename>')
def download_file(filename):
    if 'username' not in session:
        return redirect(url_for('login'))
    user_folder = get_user_folder(session['username'])
    file_path = os.path.join(user_folder, filename)
    if os.path.exists(file_path):
        return redirect(GITHUB_REPO_URL + session['username'] + '/' + filename)
    else:
        flash("Datei nicht gefunden.")
        return redirect(url_for('cloud'))

@app.route('/files')
def get_files():
    if 'username' not in session:
        return redirect(url_for('login'))
    files = load_data(session['username'])
    return jsonify(files)

@app.route('/')
def cloud():
    if 'username' not in session:
        return redirect(url_for('login'))
    files = load_data(session['username'])
    return render_template('cloud.html', files=files)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'username' not in session:
        return redirect(url_for('login'))
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)

    username = session['username']
    user_folder = get_user_folder(username)
    file_path = os.path.join(user_folder, file.filename)
    file.save(file_path)

    data = load_data(username)
    data.append(file.filename)
    save_data(username, data)

    subprocess.run(["git", "add", user_folder], check=True)
    subprocess.run(["git", "commit", "-m", f"{username} update data"], check=True)
    subprocess.run(["git", "push"], check=True)

    return redirect(url_for('cloud'))

@app.route('/delete', methods=['POST'])
def delete_file():
    if 'username' not in session:
        return redirect(url_for('login'))
    file_to_delete = request.form['file_to_delete']
    username = session['username']
    user_folder = get_user_folder(username)
    data = load_data(username)

    if file_to_delete in data:
        try:
            subprocess.run(["git", "rm", os.path.join(user_folder, file_to_delete)], check=True)
            subprocess.run(["git", "commit", "-m", f"{username} remove file {file_to_delete}"], check=True)
            subprocess.run(["git", "push"], check=True)

            data = [f for f in data if f != file_to_delete]
            save_data(username, data)
            flash(f"Datei '{file_to_delete}' wurde erfolgreich gelöscht.")
        except Exception as e:
            flash(f"Fehler beim Löschen der Datei: {e}")
    else:
        flash(f"Fehler: Datei '{file_to_delete}' wurde nicht gefunden.")

    files = load_data(username)
    return render_template('cloud.html', files=files)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)