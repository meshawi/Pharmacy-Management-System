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
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        date_of_birth = request.form['date_of_birth']
        gender = request.form['gender']
        phone_number = request.form['phone_number']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        terms = request.form.get('terms')
        privacy = request.form.get('privacy')

        if not terms or not privacy:
            flash('You must agree to the terms and conditions and privacy policy.', 'danger')
            return render_template('register.html')

        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        role = 'Customer'  # Default role, you can change this manually later in the database

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO users (first_name, last_name, date_of_birth, gender, phone_number, username, email, password, role) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (first_name, last_name, date_of_birth, gender, phone_number, username, email, hashed_password, role))
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

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form.get('email')
        phone_number = request.form.get('phone_number')
        new_password = request.form['new_password']
        hashed_password = hashlib.sha256(new_password.encode()).hexdigest()

        if not (email or phone_number):
            flash('Please provide either email or phone number.', 'danger')
            return render_template('reset_password.html')

        conn = mysql.connector.connect(**db_config)
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

@app.route('/edit_account', methods=['GET', 'POST'])
def edit_account():
    user_id = session['user_id']
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        date_of_birth = request.form['date_of_birth']
        gender = request.form['gender']
        phone_number = request.form['phone_number']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
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

@app.route('/manage_users')
@role_required('Admin')
def manage_users():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT id, first_name, last_name, date_of_birth, gender, phone_number, username, email, role 
        FROM users
    """)
    users = cursor.fetchall()

    cursor.close()
    conn.close()
    
    return render_template('manage_users.html', users=users)

@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@role_required('Admin')
def edit_user(user_id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        date_of_birth = request.form['date_of_birth']
        gender = request.form['gender']
        phone_number = request.form['phone_number']
        username = request.form['username']
        email = request.form['email']
        role = request.form['role']
        
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


@app.route('/delete_user/<int:user_id>', methods=['POST'])
@role_required('Admin')
def delete_user(user_id):
    conn = mysql.connector.connect(**db_config)
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



# Add the new routes for product management

@app.route('/products')
def view_products():
    conn = mysql.connector.connect(**db_config)
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


# Add and Edit Product Routes
@app.route('/products/add', methods=['GET', 'POST'])
@role_required('Admin')
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        stock_quantity = request.form['stock_quantity']
        category = request.form['category']
        
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO products (name, description, price, stock_quantity, category) VALUES (%s, %s, %s, %s, %s)",
                       (name, description, price, stock_quantity, category))
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
        category = request.form['category']
        
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

@app.route('/products/delete/<int:product_id>', methods=['POST'])
@role_required('Admin')
def delete_product(product_id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    try:
        # Check if the product is referenced in OrderItems
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


@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
@role_required('Customer')
def add_to_cart(product_id):
    conn = mysql.connector.connect(**db_config)
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


# View Cart and Order History Routes
@app.route('/view_cart')
@role_required('Customer')
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


@app.route('/manage_orders')
@role_required('Admin')
def manage_orders():
    conn = mysql.connector.connect(**db_config)
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

            # Convert Decimal to string
            for item in items:
                item['price'] = str(item['price'])
            order['items'] = items

            # Convert Decimal to string
            order['total_amount'] = str(order['total_amount'])

        return render_template('manage_orders.html', orders=orders)
    except Exception as e:
        print(f"Error fetching orders for management: {e}")
        return render_template('apology.html', message=f"Failed to fetch orders for management: {e}")
    finally:
        cursor.close()
        conn.close()

@app.route('/update_order_status/<int:order_id>', methods=['POST'])
@role_required('Admin')
def update_order_status(order_id):
    new_status = request.form['status']
    
    conn = mysql.connector.connect(**db_config)
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

from flask import jsonify

@app.route('/sales_report')
@role_required('Admin')
def sales_report():
    conn = mysql.connector.connect(**db_config)
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

@app.route('/inventory_report')
@role_required('Admin')
def inventory_report():
    conn = mysql.connector.connect(**db_config)
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

@app.route('/submit_review/<int:product_id>', methods=['GET', 'POST'])
@role_required('Customer')
def submit_review(product_id):
    user_id = session['user_id']
    
    if request.method == 'POST':
        rating = request.form['rating']
        review = request.form['review']
        
        conn = mysql.connector.connect(**db_config)
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


@app.route('/view_reviews/<int:product_id>')
def view_reviews(product_id):
    conn = mysql.connector.connect(**db_config)
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



if __name__ == '__main__':
    app.run(debug=True)
