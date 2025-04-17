from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import json

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Setzt einen zufälligen geheimen Schlüssel

# Konfiguration
USER_DATA_FOLDER = "user_data"

# Wenn der Ordner nicht existiert, erstelle ihn
if not os.path.exists(USER_DATA_FOLDER):
    os.makedirs(USER_DATA_FOLDER)

# Daten für jeden Benutzer speichern
def load_user_data(username):
    user_folder = os.path.join(USER_DATA_FOLDER, username)
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)
    user_data_file = os.path.join(user_folder, "data.json")
    
    if os.path.exists(user_data_file):
        with open(user_data_file, "r", encoding="utf-8") as file:
            return json.load(file)
    return []

def save_user_data(username, data):
    user_folder = os.path.join(USER_DATA_FOLDER, username)
    user_data_file = os.path.join(user_folder, "data.json")
    
    with open(user_data_file, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

@app.route('/')
def cloud():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    files = load_user_data(username)
    return render_template('cloud.html', files=files)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    
    # Datei speichern im Ordner des Benutzers
    user_folder = os.path.join(USER_DATA_FOLDER, username)
    file_path = os.path.join(user_folder, file.filename)
    file.save(file_path)
    
    # Daten aktualisieren und speichern
    files = load_user_data(username)
    files.append(file.filename)
    save_user_data(username, files)

    return redirect(url_for('cloud'))

@app.route('/delete', methods=['POST'])
def delete_file():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    file_to_delete = request.form['file_to_delete']
    
    files = load_user_data(username)
    if file_to_delete in files:
        file_path = os.path.join(USER_DATA_FOLDER, username, file_to_delete)
        os.remove(file_path)
        
        # Entfernen der Datei aus der Liste
        files = [f for f in files if f != file_to_delete]
        save_user_data(username, files)
        flash(f"Datei '{file_to_delete}' wurde erfolgreich gelöscht.")
    else:
        flash(f"Fehler: Datei '{file_to_delete}' wurde nicht gefunden.")
    
    return redirect(url_for('cloud'))

# Login- und Logout-Funktionen
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        session['username'] = username
        return redirect(url_for('cloud'))
    return render_template('login.html')

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
