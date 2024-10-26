from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random secret key
users = {}  # In-memory user storage

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.form['txt']
    password1 = request.form['pswd1']
    password2 = request.form['pswd2']

    # Check if username already exists
    if username in users:
        flash('Username already exists! Please choose a different one.')
        return redirect(url_for('index'))

    # Check if passwords match
    if password1 != password2:
        flash('Passwords do not match!')
        return redirect(url_for('index'))

    # Store user in the dictionary
    users[username] = generate_password_hash(password1)
    flash('Registration successful! You can now log in.')
    return redirect(url_for('index'))

@app.route('/login', methods=['POST'])
def login():
    username = request.form['text']
    password = request.form['pswd']

    # Check if username exists and password is correct
    if username in users and check_password_hash(users[username], password):
        session['username'] = username
        flash('Login successful!')
        return redirect(url_for('dashboard'))
    else:
        flash('Invalid username or password!')
        return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('index'))
    return f'Welcome, {session["username"]}! <br><a href="/logout">Logout</a>'

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
