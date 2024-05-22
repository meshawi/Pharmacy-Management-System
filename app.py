from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from functools import wraps
import hashlib

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# Database configuration
db_config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'pharmacy_system'
}

# Define the role_required decorator
def role_required(role):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if 'user_id' not in session or session.get('role') != role:
                return render_template('apology.html', message="You do not have permission to access this page.")
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        role = 'Customer'  # Default role, you can change this manually later in the database

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, %s)",
                           (username, email, hashed_password, role))
            conn.commit()
            flash('Registration successful. Please log in.', 'success')
            return redirect(url_for('login'))
        except mysql.connector.Error as err:
            print(err)
            return render_template('apology.html', message="Registration failed. Username or email might already be taken.")
        finally:
            cursor.close()
            conn.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, hashed_password))
            user = cursor.fetchone()
            if user:
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['role'] = user['role']
                flash('Login successful', 'success')
                return redirect(url_for('dashboard'))
            else:
                return render_template('apology.html', message="Login unsuccessful. Check username and password.")
        finally:
            cursor.close()
            conn.close()
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', role=session.get('role', 'Guest'))

@app.route('/admin')
@role_required('Admin')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/pharmacist')
@role_required('Pharmacist')
def pharmacist_dashboard():
    return render_template('pharmacist_dashboard.html')

@app.route('/customer')
@role_required('Customer')
def customer_dashboard():
    return render_template('customer_dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)
