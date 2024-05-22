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
    if 'user_id' not in session:
        return redirect(url_for('login'))
    role = session.get('role', 'Guest')
    if role == 'Admin':
        return redirect(url_for('admin_dashboard'))
    elif role == 'Pharmacist':
        return redirect(url_for('pharmacist_dashboard'))
    elif role == 'Customer':
        return redirect(url_for('customer_dashboard'))
    else:
        return render_template('apology.html', message="Invalid Role")




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

# Import MySQL connector
import mysql.connector

# Add the new routes for product management

@app.route('/products')
def view_products():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    role = session.get('role')
    return render_template('products.html', products=products, role=role)

@app.route('/products/add', methods=['GET', 'POST'])
@role_required('Admin')
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        stock_quantity = request.form['stock_quantity']
        
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO products (name, description, price, stock_quantity) VALUES (%s, %s, %s, %s)",
                       (name, description, price, stock_quantity))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Product added successfully.', 'success')
        return redirect(url_for('view_products'))
    
    return render_template('add_product.html')

@app.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
@role_required('Admin')
def edit_product(product_id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        stock_quantity = request.form['stock_quantity']
        
        cursor.execute("UPDATE products SET name=%s, description=%s, price=%s, stock_quantity=%s WHERE id=%s",
                       (name, description, price, stock_quantity, product_id))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Product updated successfully.', 'success')
        return redirect(url_for('view_products'))
    
    cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
    product = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('edit_product.html', product=product)

@app.route('/products/delete/<int:product_id>', methods=['POST'])
@role_required('Admin')
def delete_product(product_id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Product deleted successfully.', 'success')
    return redirect(url_for('view_products'))

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
@role_required('Customer')
def add_to_cart(product_id):
    if 'cart' not in session:
        session['cart'] = []

    session['cart'].append(product_id)
    flash('Product added to cart.', 'success')
    return redirect(url_for('view_products'))


@app.route('/view_cart')
def view_cart():
    if 'cart' not in session:
        session['cart'] = []

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    products = []
    total_amount = 0
    for product_id in session['cart']:
        cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
        product = cursor.fetchone()
        products.append(product)
        total_amount += product['price']
    cursor.close()
    conn.close()
    return render_template('view_cart.html', products=products, total_amount=total_amount)

@app.route('/confirm_order', methods=['POST'])
@role_required('Customer')
def confirm_order():
    if 'cart' not in session or not session['cart']:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('view_cart'))

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    total_amount = 0
    for product_id in session['cart']:
        cursor.execute("SELECT price FROM products WHERE id = %s", (product_id,))
        price = cursor.fetchone()[0]
        total_amount += price

    try:
        # Start transaction
        cursor.execute("START TRANSACTION")

        # Insert order into Orders table
        cursor.execute("INSERT INTO Orders (customer_id, total_amount) VALUES (%s, %s)",
                       (session['user_id'], total_amount))
        order_id = cursor.lastrowid

        # Insert items into OrderItems table
        for product_id in session['cart']:
            cursor.execute("SELECT price FROM products WHERE id = %s", (product_id,))
            price = cursor.fetchone()[0]
            cursor.execute("INSERT INTO OrderItems (order_id, product_id, quantity, price) VALUES (%s, %s, %s, %s)",
                           (order_id, product_id, 1, price))
            cursor.execute("UPDATE products SET stock_quantity = stock_quantity - 1 WHERE id = %s", (product_id,))

        # Commit transaction
        cursor.execute("COMMIT")

        session['cart'] = []  # Clear cart after successful order
        flash('Order confirmed successfully.', 'success')
        return redirect(url_for('view_order_history'))
    except mysql.connector.Error as err:
        cursor.execute("ROLLBACK")
        print(err)
        flash('Failed to confirm order.', 'danger')
        return redirect(url_for('view_cart'))
    finally:
        cursor.close()
        conn.close()


@app.route('/view_order_history')
@role_required('Customer')
def view_order_history():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT * FROM Orders WHERE customer_id = %s ORDER BY order_date DESC", (session['user_id'],))
        orders = cursor.fetchall()

        for order in orders:
            cursor.execute("""
                SELECT p.name, p.description, oi.quantity, oi.price 
                FROM OrderItems oi 
                JOIN products p ON oi.product_id = p.id 
                WHERE oi.order_id = %s
            """, (order['id'],))
            items = cursor.fetchall()

            # Convert Decimal to string
            for item in items:
                item['price'] = str(item['price'])
            order['items'] = items

            # Convert Decimal to string
            order['total_amount'] = str(order['total_amount'])

        print("Final orders data structure:", orders)
        return render_template('view_order_history.html', orders=orders)
    except Exception as e:
        print(f"Error fetching order history: {e}")
        return render_template('apology.html', message=f"Failed to fetch order history: {e}")
    finally:
        cursor.close()
        conn.close()






if __name__ == '__main__':
    app.run(debug=True)
