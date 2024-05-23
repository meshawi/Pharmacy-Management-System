# Pharmacy Management System - Code Details

## Introduction

This document provides a detailed explanation of the code structure and functionality of the Pharmacy Management System. This project was developed as part of the CS50 final project by Mohammed Aleshawi.

## Project Structure

The project is organized into several key files and directories, each serving a specific purpose in the application:

### `app.py`

This is the main application file that initializes the Flask app and defines the routes for the application.

- **Initialization**: Sets up the Flask application and configuration.
- **Routes**: Contains all the route definitions for handling HTTP requests and rendering templates.
  Key sections:
- **Database Configuration**: Configures the connection to the MySQL database.

### `templates/`

This directory contains all the HTML templates used in the project. Each template extends the base layout and defines specific content for different pages.

- **`base.html`**: The base layout template that includes common elements like the header, footer, and navigation bar.
- **`login.html`**: The template for the login page.
- **`register.html`**: The template for the registration page.
- **`dashboard.html`**: The template for the user dashboard.
- **`admin_dashboard.html`**: The template for the admin dashboard.
- **`pharmacist_dashboard.html`**: The template for the pharmacist dashboard.
- **`customer_dashboard.html`**: The template for the customer dashboard.
- **`reset_password.html`**: The template for the password reset page.
- **`view_products.html`**: The template for viewing products.
- **`add_product.html`**: The template for adding a new product.
- **`edit_product.html`**: The template for editing a product.
- **`view_cart.html`**: The template for viewing the cart.
- **`view_order_history.html`**: The template for viewing order history.
- **`manage_users.html`**: The template for managing users.
- **`manage_orders.html`**: The template for managing orders.
- **`sales_report.html`**: The template for viewing the sales report.
- **`inventory_report.html`**: The template for viewing the inventory report.
- **`submit_review.html`**: The template for submitting product reviews.
- **`view_reviews.html`**: The template for viewing product reviews.

### `static/`

This directory contains static files like CSS, JavaScript, and images.

- **`styles.css`**: Custom CSS for styling the application.
- **`anim.json`**: JSON file for Lottie animations.

### `database.sql`

This SQL file contains the schema for the database used in the project. It defines the tables and relationships between them.

## Detailed Code Explanation

### `app.py`

#### Initialization

```python
# app.py
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

# Utility function to connect to the database
def get_db_connection():
    return mysql.connector.connect(**db_config)

#
```

This snippet initializes the Flask application and sets up the configuration for the MySQL database connection
.get_db_connection: A function that establishes and returns a connection to the MySQL database using the db_config dictionary.

#### Decorators for Role-Based Access Control

```python
# app.py
def role_required(role):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if 'user_id' not in session or session.get('role') != role:
                return render_template('apology.html', message="You do not have permission to access this page.")
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper


```

role_required(role): A decorator function that checks if the user has the required role to access a particular view. If the user does not have the required role, it renders an apology page with an error message.

# Auth Routes

#### Registration Route

```python
# app.py
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Extract form data
        form_data = request.form
        first_name = form_data['first_name'].strip()
        last_name = form_data['last_name'].strip()
        date_of_birth = form_data['date_of_birth']
        gender = form_data['gender']
        phone_number = form_data['phone_number'].strip()
        username = form_data['username'].strip()
        email = form_data['email'].strip()
        password = form_data['password']
        terms = form_data.get('terms')
        privacy = form_data.get('privacy')

        # Check terms and privacy
        if not terms or not privacy:
            flash('You must agree to the terms and conditions and privacy policy.', 'danger')
            return render_template('register.html')

        # Validate that all fields are filled
        if not (first_name and last_name and date_of_birth and gender and phone_number and username and email and password):
            flash('Please fill in all fields.', 'danger')
            return render_template('register.html')

        # Validate email format
        if "@" not in email or "." not in email:
            flash('Invalid email format.', 'danger')
            return render_template('register.html')

        # Check password strength (example: at least 8 characters)
        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'danger')
            return render_template('register.html')

        # Hash the password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        role = 'Customer'  # Default role

        # Database operations
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Check if username or email already exists
            cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, email))
            if cursor.fetchone():
                flash('Username or email already in use. Please choose another one.', 'danger')
                return render_template('register.html')

            # Insert new user
            cursor.execute("""
                INSERT INTO users (first_name, last_name, date_of_birth, gender, phone_number, username, email, password, role)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (first_name, last_name, date_of_birth, gender, phone_number, username, email, hashed_password, role))
            conn.commit()
            flash('Registration successful. Please log in.', 'success')
            return redirect(url_for('login'))
        except mysql.connector.Error as err:
            print(err)
            flash('Registration failed due to a system error. Please try again later.', 'danger')
        finally:
            cursor.close()
            conn.close()
    return render_template('register.html')
```

- Route Definition: Defines the /register route which handles both GET and POST requests.
- Form Handling: Extracts form data submitted by the user.
- Terms and Privacy Check: Ensures that the user agrees to the terms and - conditions and privacy policy.
- Password Hashing: Uses SHA-256 to hash the user's password for secure storage.
- Database Insertion: Inserts the new user's data into the users table in the database.
- Error Handling: Catches and handles any database errors during registration and Valedation.

#### Login Route

```python
# app.py
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        conn = get_db_connection()
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
```

- Route Definition: Defines the /login route which handles both GET and POST requests.
- Form Handling: Extracts the username and password submitted by the user.
- Password Hashing: Hashes the submitted password to compare with the stored hashed password.
- User Authentication: Queries the database to check if the username and hashed password match any records.
- Session Management: Stores the user's ID, username, and role in the session upon successful login.

#### Logout Route

```python
# app.py
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))
```

- Route Definition: Defines the /logout route.
- Session Management: Clears the session data to log the user out.
- Flash Message: Displays a success message upon logout.

#### Reset Password Route

```python
# app.py
@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        form_data = request.form
        username = form_data['username']
        email = form_data.get('email')
        phone_number = form_data.get('phone_number')
        new_password = form_data['new_password']
        hashed_password = hashlib.sha256(new_password.encode()).hexdigest()

        if not (email or phone_number):
            flash('Please provide either email or phone number.', 'danger')
            return render_template('reset_password.html')

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            if email:
                cursor.execute("SELECT * FROM users WHERE username = %s AND email = %s", (username, email))
            else:
                cursor.execute("SELECT * FROM users WHERE username = %s AND phone_number = %s", (username, phone_number))

            user = cursor.fetchone()

            if user:
                cursor.execute("UPDATE users SET password = %s WHERE username = %s", (hashed_password, username))
                conn.commit()
                flash('Password reset successfully. Please log in with your new password.', 'success')
                return redirect(url_for('login'))
            else:
                flash('User not found. Please check your details and try again.', 'danger')
        except mysql.connector.Error as err:
            print(err)
            flash('Failed to reset password. Please try again later.', 'danger')
        finally:
            cursor.close()
            conn.close()

    return render_template('reset_password.html')
```

- Route Definition: Defines the /reset_password route which handles both GET and POST requests.
- Form Handling: Extracts the username, email, phone number, and new password submitted by the user.
  Password Hashing: Hashes the new password.
- User Verification: Verifies the user's details using either the email or phone number.
- Password Update: Updates the user's password in the database if the user is found.

#### User Account Editing Route

```python
# app.py
@app.route('/edit_account', methods=['GET', 'POST'])
def edit_account():
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        form_data = request.form
        first_name = form_data['first_name']
        last_name = form_data['last_name']
        date_of_birth = form_data['date_of_birth']
        gender = form_data['gender']
        phone_number = form_data['phone_number']
        username = form_data['username']
        email = form_data['email']
        password = form_data['password']

        if password:
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            cursor.execute("""
                UPDATE users
                SET first_name = %s, last_name = %s, date_of_birth = %s, gender = %s, phone_number = %s, username = %s, email = %s, password = %s
                WHERE id = %s
            """, (first_name, last_name, date_of_birth, gender, phone_number, username, email, hashed_password, user_id))
        else:
            cursor.execute("""
                UPDATE users
                SET first_name = %s, last_name = %s, date_of_birth = %s, gender = %s, phone_number = %s, username = %s, email = %s
                WHERE id = %s
            """, (first_name, last_name, date_of_birth, gender, phone_number, username, email, user_id))

        conn.commit()
        flash('Account updated successfully.', 'success')
        return redirect(url_for('customer_dashboard'))

    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    return render_template('edit_account.html', user=user)
```

- Route Definition: Defines the /edit_account route for both GET and POST requests.
- Form Handling: Extracts user data from the form and updates the user's information in the database.
- Password Hashing: Hashes the new password if it is provided.
- Database Update: Updates the user's details in the users table.

#### Dashboard Routes

```python
# app.py
@app.route('/')
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

```

- Route Definition: Defines the / route for the main dashboard.
- Role-Based Redirection: Redirects users to the appropriate dashboard based on their role.

#### Role-Based Dashboards

```python
# app.py
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

```

- Defines separate routes for the admin, pharmacist, and customer dashboards, ensuring that only users with the appropriate role can access each dashboard using the role_required decorator.

# User Management Routes

#### Managing Users (Admin Only)

```python
# app.py
@app.route('/manage_users')
@role_required('Admin')
def manage_users():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT id, first_name, last_name, date_of_birth, gender, phone_number, username, email, role
        FROM users
    """)
    users = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('manage_users.html', users=users)
```

- Route Definition: Defines the /manage_users route, accessible only by Admin users.
- Fetching Users: Retrieves all user details from the database.
- Rendering Template: Displays the user management page with the list of users.

#### Editing a User (Admin Only)

```python
# app.py
@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@role_required('Admin')
def edit_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        form_data = request.form
        first_name = form_data['first_name']
        last_name = form_data['last_name']
        date_of_birth = form_data['date_of_birth']
        gender = form_data['gender']
        phone_number = form_data['phone_number']
        username = form_data['username']
        email = form_data['email']
        role = form_data['role']

        cursor.execute("""
            UPDATE users
            SET first_name = %s, last_name = %s, date_of_birth = %s, gender = %s, phone_number = %s, username = %s, email = %s, role = %s
            WHERE id = %s
        """, (first_name, last_name, date_of_birth, gender, phone_number, username, email, role, user_id))

        conn.commit()
        flash('User updated successfully.', 'success')
        return redirect(url_for('manage_users'))

    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    return render_template('edit_user.html', user=user)


```

- Route Definition: Defines the /edit_user/<int:user_id> route for editing user details, accessible only by Admin users.
- Form Handling: Extracts and updates the user's details in the database.
- Rendering Template: Displays the edit user page with the current user details.

#### Deleting a User (Admin Only)

```python
# app.py
@app.route('/delete_user/<int:user_id>', methods=['POST'])
@role_required('Admin')
def delete_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        flash('User deleted successfully.', 'success')
    except mysql.connector.Error as err:
        conn.rollback()
        print(err)
        flash('Failed to delete user.', 'danger')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('manage_users'))


```

- Route Definition: Defines the /delete_user/<int:user_id> route for deleting users, accessible only by Admin users.
- Database Deletion: Deletes the user from the database.
- Error Handling: Handles any errors that occur during the deletion process.

# Product Management Routes

#### Viewing Products

```python
# app.py
@app.route('/products')
def view_products():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    cursor.execute("SELECT DISTINCT category FROM products")
    categories = cursor.fetchall()
    categories = [category['category'] for category in categories]

    for product in products:
        cursor.execute("""
            SELECT AVG(rating) as average_rating
            FROM reviews
            WHERE product_id = %s
        """, (product['id'],))
        result = cursor.fetchone()
        product['average_rating'] = result['average_rating'] if result['average_rating'] else 'No ratings'

    cursor.close()
    conn.close()
    role = session.get('role')
    return render_template('products.html', products=products, role=role, categories=categories)
```

- Route Definition: Defines the /products route for viewing products.
- Fetching Products: Retrieves all products and their categories from the database.
- Calculating Average Rating: Computes the average rating for each product.
- Rendering Template: Displays the products page with the list of products and categories.

Adding a Product (Admin and Pharmacist Only)

```python
# app.py
@app.route('/products/add', methods=['GET', 'POST'])
@role_required('Admin', 'Pharmacist')
def add_product():
    if request.method == 'POST':
        form_data = request.form
        name = form_data['name']
        description = form_data['description']
        price = form_data['price']
        stock_quantity = form_data['stock_quantity']
        category = form_data['category']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO products (name, description, price, stock_quantity, category) VALUES (%s, %s, %s, %s, %s)",
                       (name, description, price, stock_quantity, category))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Product added successfully.', 'success')
        return redirect(url_for('view_products'))

    return render_template('add_product.html')
```

- Route Definition: Defines the /products/add route for adding new products, accessible only by Admin users.
- Form Handling: Extracts and inserts the new product details into the database.
- Rendering Template: Displays the add product page.

#### Editing a Product (Admin Only)

```python
# app.py
@app.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
@role_required('Admin')
def edit_product(product_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        form_data = request.form
        name = form_data['name']
        description = form_data['description']
        price = form_data['price']
        stock_quantity = form_data['stock_quantity']
        category = form_data['category']

        cursor.execute("UPDATE products SET name=%s, description=%s, price=%s, stock_quantity=%s, category=%s WHERE id=%s",
                       (name, description, price, stock_quantity, category, product_id))
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
```

- Route Definition: Defines the /products/edit/<int:product_id> route for editing product details, accessible only by Admin users.
- Form Handling: Extracts and updates the product details in the database.
- Rendering Template: Displays the edit product page with the current product details.

#### Deleting a Product (Admin Only)

```python
# app.py
@app.route('/products/delete/<int:product_id>', methods=['POST'])
@role_required('Admin')
def delete_product(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT COUNT(*) FROM OrderItems WHERE product_id = %s", (product_id,))
        count = cursor.fetchone()[0]

        if count > 0:
            flash('Cannot delete product because it is referenced in order items.', 'danger')
        else:
            cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
            conn.commit()
            flash('Product deleted successfully.', 'success')
    except mysql.connector.Error as err:
        conn.rollback()
        print(err)
        flash('Failed to delete product.', 'danger')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('view_products'))


```

- Route Definition: Defines the /products/delete/<int:product_id> route for deleting products, accessible only by Admin users.
- Database Deletion: Deletes the product from the database if it is not referenced in any order items.
- Error Handling: Handles any errors that occur during the deletion process.

# Cart and Order Routes

#### Adding to Cart (Customer Only)

```python
# app.py
@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
@role_required('Customer')
def add_to_cart(product_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT stock_quantity FROM products WHERE id = %s", (product_id,))
        product = cursor.fetchone()

        if product['stock_quantity'] < 1:
            flash('Product is out of stock and cannot be added to the cart.', 'danger')
        else:
            if 'cart' not in session:
                session['cart'] = []
            session['cart'].append(product_id)
            flash('Product added to cart.', 'success')
    except mysql.connector.Error as err:
        print(err)
        flash('Failed to add product to cart.', 'danger')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('view_products'))


```

- Route Definition: Defines the /add_to_cart/<int:product_id> route for adding products to the cart, accessible only by Customer users.
- Stock Check: Checks if the product is in stock before adding it to the cart.
- Session Management: Adds the product ID to the cart stored in the session.

#### Removing from Cart (Customer Only)

```python
# app.py
@app.route('/remove_from_cart/<int:product_id>', methods=['POST'])
@role_required('Customer')
def remove_from_cart(product_id):
    if 'cart' in session:
        try:
            session['cart'].remove(product_id)
            flash('Product removed from cart.', 'success')
        except ValueError:
            flash('Product not found in cart.', 'danger')
    else:
        flash('Cart is empty.', 'warning')
    return redirect(url_for('view_cart'))


```

- Route Definition: Defines the /remove_from_cart/<int:product_id> route for removing products from the cart, accessible only by Customer users.
- Session Management: Removes the product ID from the cart stored in the session.

#### Viewing Cart (Customer Only)

```python
# app.py
@app.route('/view_cart')
@role_required('Customer')
def view_cart():
    if 'cart' not in session:
        session['cart'] = []

    conn = get_db_connection()
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
```

- Route Definition: Defines the /view_cart route for viewing the cart, accessible only by Customer users.
- Fetching Products: Retrieves the products in the cart from the database.
- Calculating Total: Computes the total amount for the products in the cart.
- Rendering Template: Displays the cart page with the list of products and the total amount.

#### Confirming Order (Customer Only)

```python
# app.py
@app.route('/confirm_order', methods=['POST'])
@role_required('Customer')
def confirm_order():
    if 'cart' not in session or not session['cart']:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('view_cart'))

    conn = get_db_connection()
    cursor = conn.cursor()

    total_amount = 0
    for product_id in session['cart']:
        cursor.execute("SELECT price FROM products WHERE id = %s", (product_id,))
        price = cursor.fetchone()[0]
        total_amount += price

    try:
        cursor.execute("START TRANSACTION")

        cursor.execute("INSERT INTO Orders (customer_id, total_amount) VALUES (%s, %s)", (session['user_id'], total_amount))
        order_id = cursor.lastrowid

        for product_id in session['cart']:
            cursor.execute("SELECT price FROM products WHERE id = %s", (product_id,))
            price = cursor.fetchone()[0]
            cursor.execute("INSERT INTO OrderItems (order_id, product_id, quantity, price) VALUES (%s, %s, %s, %s)",
                           (order_id, product_id, 1, price))
            cursor.execute("UPDATE products SET stock_quantity = stock_quantity - 1 WHERE id = %s", (product_id,))

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


```

- Route Definition: Defines the /confirm_order route for confirming orders, accessible only by Customer users.
- Transaction Management: Uses transactions to ensure the order is processed correctly.
- Order Confirmation: Inserts the order and order items into the database, updates product stock, and clears the cart upon success.

#### Viewing Order History (Customer Only)

```python
# app.py
@app.route('/view_order_history')
@role_required('Customer')
def view_order_history():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM Orders WHERE customer_id = %s ORDER BY order_date DESC", (session['user_id'],))
        orders = cursor.fetchall()

        for order in orders:
            cursor.execute("""
                SELECT p.id as product_id, p.name, p.description, p.category, oi.quantity, oi.price
                FROM OrderItems oi
                JOIN products p ON oi.product_id = p.id
                WHERE oi.order_id = %s
            """, (order['id'],))
            items = cursor.fetchall()

            for item in items:
                item['price'] = str(item['price'])
            order['items'] = items
            order['total_amount'] = str(order['total_amount'])

        return render_template('view_order_history.html', orders=orders)
    except Exception as e:
        print(f"Error fetching order history: {e}")
        return render_template('apology.html', message=f"Failed to fetch order history: {e}")
    finally:
        cursor.close()
        conn.close()


```

- Route Definition: Defines the /view_order_history route for viewing order history, accessible only by Customer users.
- Fetching Orders: Retrieves the customer's orders and their details from the database.
- Rendering Template: Displays the order history page with the list of orders and their items.

# Admin Order Management Routes

#### Managing Orders (Admin Only)

```python
# app.py

@app.route('/manage_orders')
@role_required('Admin')
def manage_orders():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM Orders ORDER BY order_date DESC")
        orders = cursor.fetchall()

        for order in orders:
            cursor.execute("""
                SELECT p.name, p.description, oi.quantity, oi.price
                FROM OrderItems oi
                JOIN products p ON oi.product_id = p.id
                WHERE oi.order_id = %s
            """, (order['id'],))
            items = cursor.fetchall()

            for item in items:
                item['price'] = str(item['price'])
            order['items'] = items
            order['total_amount'] = str(order['total_amount'])

        return render_template('manage_orders.html', orders=orders)
    except Exception as e:
        print(f"Error fetching orders for management: {e}")
        return render_template('apology.html', message=f"Failed to fetch orders for management: {e}")
    finally:
        cursor.close()
        conn.close()

```

- Route Definition: Defines the /manage_orders route for managing orders, accessible only by Admin users.
- Fetching Orders: Retrieves all orders and their details from the database.
- Rendering Template: Displays the manage orders page with the list of orders and their items.

#### Updating Order Status (Admin Only)

```python
# app.py
@app.route('/update_order_status/<int:order_id>', methods=['POST'])
@role_required('Admin')
def update_order_status(order_id):
    new_status = request.form['status']

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("UPDATE Orders SET status = %s WHERE id = %s", (new_status, order_id))
        conn.commit()
        flash('Order status updated successfully.', 'success')
    except Exception as e:
        conn.rollback()
        print(f"Error updating order status: {e}")
        flash('Failed to update order status.', 'danger')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('manage_orders'))


```

- Route Definition: Defines the /update_order_status/<int:order_id> route for updating the order status, accessible only by Admin users.
- Status Update: Updates the status of the specified order in the database.
- Error Handling: Handles any errors that occur during the update process.

# Reporting Routes

#### Sales Report (Admin Only)

```python
# app.py
@app.route('/sales_report')
@role_required('Admin')
def sales_report():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                DATE(order_date) as order_date,
                SUM(total_amount) as total_sales,
                COUNT(id) as total_orders
            FROM Orders
            GROUP BY DATE(order_date)
            ORDER BY order_date DESC
        """)
        sales_data = cursor.fetchall()
        return render_template('sales_report.html', sales_data=sales_data)
    except Exception as e:
        print(f"Error fetching sales report: {e}")
        return render_template('apology.html', message=f"Failed to fetch sales report: {e}")
    finally:
        cursor.close()
        conn.close()


```

- Route Definition: Defines the /sales_report route for viewing the sales report, accessible only by Admin users.
- Fetching Sales Data: Retrieves sales data grouped by order date from the database.
- Rendering Template: Displays the sales report page with the sales data.

#### Inventory Report (Admin Only)

```python
# app.py
@app.route('/inventory_report')
@role_required('Admin')
def inventory_report():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                p.id,
                p.name,
                p.description,
                p.price,
                p.stock_quantity,
                SUM(oi.quantity) as total_sold
            FROM products p
            LEFT JOIN OrderItems oi ON p.id = oi.product_id
            GROUP BY p.id
            ORDER BY p.name
        """)
        inventory_data = cursor.fetchall()
        return render_template('inventory_report.html', inventory_data=inventory_data)
    except Exception as e:
        print(f"Error fetching inventory report: {e}")
        return render_template('apology.html', message=f"Failed to fetch inventory report: {e}")
    finally:
        cursor.close()
        conn.close()


```

- Route Definition: Defines the /inventory_report route for viewing the inventory report, accessible only by Admin users.
- Fetching Inventory Data: Retrieves inventory data, including total sold quantities, from the database.
- Rendering Template: Displays the inventory report page with the inventory data.

# Review Routes

#### Submitting a Review (Customer Only)

```python
# app.py
@app.route('/submit_review/<int:product_id>', methods=['GET', 'POST'])
@role_required('Customer')
def submit_review(product_id):
    user_id = session['user_id']

    if request.method == 'POST':
        rating = request.form['rating']
        review = request.form['review']

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO reviews (user_id, product_id, rating, review)
                VALUES (%s, %s, %s, %s)
            """, (user_id, product_id, rating, review))
            conn.commit()
            flash('Review submitted successfully.', 'success')
            return redirect(url_for('view_order_history'))
        except mysql.connector.Error as err:
            print(err)
            flash('Failed to submit review.', 'danger')
        finally:
            cursor.close()
            conn.close()

    return render_template('submit_review.html', product_id=product_id)

```

- Route Definition: Defines the /submit_review/<int:product_id> route for submitting reviews, accessible only by Customer users.
- Form Handling: Extracts the rating and review text from the form and inserts them into the database.
- Rendering Template: Displays the submit review page with the product ID.

#### Viewing Reviews

```python
# app.py
@app.route('/view_reviews/<int:product_id>')
def view_reviews(product_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT r.rating, r.review, r.created_at, u.username
        FROM reviews r
        JOIN users u ON r.user_id = u.id
        WHERE r.product_id = %s
        ORDER BY r.created_at DESC
    """, (product_id,))
    reviews = cursor.fetchall()

    cursor.execute("SELECT name FROM products WHERE id = %s", (product_id,))
    product = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template('view_reviews.html', reviews=reviews, product=product)


```

- Route Definition: Defines the /view_reviews/<int:product_id> route for viewing reviews of a specific product.
- Fetching Reviews: Retrieves the reviews for the specified product from the database.
- Rendering Template: Displays the view reviews page with the list of reviews and product details.

#### Miscellaneous Routes

```python
# app.py
@app.route('/contact_us')
def contact_us():
    return render_template('contact_us.html')

@app.route('/about_us')
def about_us():
    return render_template('about_us.html')

@app.route('/terms_and_conditions')
def terms_and_conditions():
    return render_template('terms_and_conditions.html')

@app.route('/privacy_policy')
def privacy_policy():
    return render_template('privacy_policy.html')


```

- Miscellaneous Routes: Defines routes for the contact us, about us, terms and conditions, and privacy policy pages.
- Rendering Templates: Displays the respective static pages.

#### Main Entry Point

```python
# app.py

# Main
if __name__ == '__main__':
    app.run(debug=True)

```

- Main Entry Point: Starts the Flask application in debug mode, allowing for real-time code changes and error tracking.

# Other Files

#### Base Layout

```html
<!-- base.html -->
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{% block title %}Pharmacy System{% endblock %}</title>
    <link
      rel="stylesheet"
      href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css"
    />
    <link
      rel="stylesheet"
      href="{{ url_for('static', filename='styles.css') }}"
    />
    <link
      rel="stylesheet"
      href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css"
    />
  </head>
  <body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
      <a class="navbar-brand" href="{{ url_for('dashboard') }}"
        >Pharmacy System</a
      >
      <button
        class="navbar-toggler"
        type="button"
        data-toggle="collapse"
        data-target="#navbarNav"
        aria-controls="navbarNav"
        aria-expanded="false"
        aria-label="Toggle navigation"
      >
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav mr-auto">
          {% if session.get('user_id') %}
          <li class="nav-item">
            <a class="nav-link" href="{{ url_for('dashboard') }}"
              ><i class="fas fa-home"></i> Home</a
            >
          </li>
          <li class="nav-item">
            <a class="nav-link" href="{{ url_for('view_products') }}"
              ><i class="fas fa-boxes"></i> Products</a
            >
          </li>
          {% if session.get('role') == 'Customer' %}
          <li class="nav-item">
            <a class="nav-link" href="{{ url_for('view_cart') }}"
              ><i class="fas fa-shopping-cart"></i> Cart</a
            >
          </li>
          <li class="nav-item">
            <a class="nav-link" href="{{ url_for('view_order_history') }}"
              ><i class="fas fa-history"></i> Order History</a
            >
          </li>
          {% endif %} {% if session.get('role') in ['Admin', 'Pharmacist'] %}
          <li class="nav-item">
            <a class="nav-link" href="{{ url_for('manage_orders') }}"
              ><i class="fas fa-receipt"></i> Manage Orders</a
            >
          </li>
          {% endif %} {% if session.get('role') == 'Admin' %}
          <li class="nav-item">
            <a class="nav-link" href="{{ url_for('manage_users') }}"
              ><i class="fas fa-users-cog"></i> Manage Users</a
            >
          </li>
          <li class="nav-item">
            <a class="nav-link" href="{{ url_for('sales_report') }}"
              ><i class="fas fa-chart-line"></i> Sales Report</a
            >
          </li>
          <li class="nav-item">
            <a class="nav-link" href="{{ url_for('inventory_report') }}"
              ><i class="fas fa-warehouse"></i> Inventory Report</a
            >
          </li>
          {% endif %} {% endif %}
        </ul>

        <ul class="navbar-nav ml-auto">
          {% if session.get('user_id') %}
          <li class="nav-item dropdown">
            <a
              class="nav-link dropdown-toggle"
              href="#"
              id="navbarDropdown"
              role="button"
              data-toggle="dropdown"
              aria-haspopup="true"
              aria-expanded="false"
            >
              <i class="fas fa-user"></i> {{ session['username'] }}
            </a>
            <div
              class="dropdown-menu dropdown-menu-right"
              aria-labelledby="navbarDropdown"
            >
              <a class="dropdown-item" href="{{ url_for('edit_account') }}"
                ><i class="fas fa-user-edit"></i> Edit Account</a
              >
              <div class="dropdown-divider"></div>
              <a class="dropdown-item" href="{{ url_for('logout') }}"
                ><i class="fas fa-sign-out-alt"></i> Logout</a
              >
            </div>
          </li>
          {% else %}
          <li class="nav-item">
            <a class="nav-link" href="{{ url_for('login') }}"
              ><i class="fas fa-sign-in-alt"></i> Login</a
            >
          </li>
          <li class="nav-item">
            <a class="nav-link" href="{{ url_for('register') }}"
              ><i class="fas fa-user-plus"></i> Register</a
            >
          </li>
          {% endif %}
        </ul>
      </div>
    </nav>

    <div class="container mt-5">
      {% with messages = get_flashed_messages(with_categories=true) %} {% if
      messages %}
      <div class="mt-3">
        {% for category, message in messages %}
        <div class="alert alert-{{ category }}">{{ message }}</div>
        {% endfor %}
      </div>
      {% endif %} {% endwith %} {% block content %}{% endblock %}
    </div>
    <footer>
      <div class="footer_container">
        <p>&copy; 2024 Pharmacy System. All rights reserved.</p>
        <p>
          <a href="{{ url_for('dashboard') }}">Home</a> |
          <a href="{{ url_for('view_products') }}">Products</a> |
          <a href="{{ url_for('contact_us') }}">Contact Us</a> |
          <a href="{{ url_for('about_us') }}">About Us</a>
        </p>
      </div>
    </footer>

    <script src="https://code.jquery.com/jquery-3.3.1.slim.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js"></script>
  </body>
</html>
```

- DOCTYPE and HTML Structure: Defines the document type and basic HTML structure.
- Head Section: Contains metadata and links to external stylesheets (Bootstrap, Font Awesome, custom CSS).
- Navigation Bar: Includes links to various pages with conditional links based on user role (Admin, Pharmacist, Customer).
- Container for Page Content: Uses Bootstrap for styling; includes placeholders for flash messages and content blocks.
- Footer: Contains links to the home, products, contact us, and about us pages, styled with CSS.
- JavaScript Includes: Links to jQuery, Popper.js, and Bootstrap JavaScript files for interactivity.

#### Base Layout

```html
<!-- apology.html -->
{% extends "base.html" %} {% block title %}Apology{% endblock %} {% block
content %}
<div class="container text-center mt-5">
  <h1>Sorry!</h1>
  <p>{{ message }}</p>
  <a href="{{ url_for('login') }}" class="btn btn-primary">Go back to login</a>
</div>
{% endblock %}
```

- Template Extension: Inherits the structure and styles from base.html.
- Title Block: Sets the page title to "Apology".
- Content Block: Displays a message passed from the backend and provides a link to go back to the login page.

#### Global Styles

```css
/* styles.css */
body {
  background-color: #f8f9fa;
}

.navbar {
  margin-bottom: 30px;
}

.container {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

h1,
h2 {
  color: #343a40;
}

.table th,
.table td {
  vertical-align: middle !important;
}

.card {
  margin-bottom: 20px;
}

.card-header {
  background: #007bff;
  color: #fff;
  border-bottom: 1px solid #007bff;
}

.card-body {
  background: #f8f9fa;
}

.btn-primary {
  background-color: #007bff;
  border-color: #007bff;
}

.btn-primary:hover {
  background-color: #0056b3;
  border-color: #004085;
}
.footer_container {
  flex: 1;
}
footer {
  background-color: #343a40;
  color: white;
  padding: 20px 0;
  position: fixed;
  bottom: 0;
  width: 100%;
  text-align: center;
}
footer a {
  color: #ffffff;
  margin: 0 10px;
  text-decoration: none;
}
footer a:hover {
  text-decoration: underline;
}
```

- Body Background: Sets the background color for the entire page.
- Navbar Styling: Adds margin to the bottom of the navbar.
- Container Styling: Styles the main container with a white background, padding, rounded corners, and a box shadow.
- Header Styling: Sets the color for h1 and h2 elements.
- Table Styling: Ensures vertical alignment for table cells.
- Card Styling: Adds margin to the bottom of card elements.
- Card Header Styling: Styles the card header with a blue background and white text.
- Card Body Styling: Sets the background color for card bodies.
- Primary Button Styling: Customizes the appearance of primary buttons, including hover effects.
- Footer Styling: Styles the footer with a dark background, white text, and fixed positioning at the bottom of the page.

# Conclusion

The app.py file for the Pharmacy Management System is comprehensive and covers a wide range of functionalities, including user management, product management, cart and order management, review submission and viewing, and various reports. Each route is carefully defined with role-based access control and error handling to ensure the application runs smoothly and securely and for the other files they encapsulate the key elements and functionalities of each file, providing a quick reference to their roles in the Pharmacy Management System.
