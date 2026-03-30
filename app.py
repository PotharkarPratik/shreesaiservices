from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import mysql.connector
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

# ---------- LOAD ENV ----------
load_dotenv("pass.env") if os.path.exists("pass.env") else None
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# ---------- FLASK ----------
app = Flask(__name__)
app.secret_key = "FLASK_SECRET_KEY"

# ---------- DATABASE CONNECTION ----------
def get_db_connection():
    try:
        return mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
    except mysql.connector.Error as e:
        print("Database connection failed:", e)
        return None

# ---------- ADMIN LOGIN ----------
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# ---------- EMAIL FUNCTIONS ----------
def send_customer_email(email, name, product):
    try:
        msg = MIMEMultipart()
        msg["From"] = ADMIN_EMAIL
        msg["To"] = email
        msg["Subject"] = "Order Confirmation - Shree Sai Services"

        body = f"""
Hello {name},

Your order has been placed successfully.

Product: {product}

Our team will contact you soon.

Thank you,
Shree Sai Services
"""
        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(ADMIN_EMAIL, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print("Customer email failed:", e)


def send_admin_email(order):
    try:
        msg = MIMEMultipart()
        msg["From"] = ADMIN_EMAIL
        msg["To"] = ADMIN_EMAIL
        msg["Subject"] = "New Order Received"

        body = f"""
New Order Received

Product: {order['product_name']}
Customer: {order['customer_name']}
Phone: {order['customer_phone']}
Email: {order['customer_email']}
Address: {order['customer_address']}
"""
        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(ADMIN_EMAIL, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print("Admin email failed:", e)


# ================= ROUTES =================

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/services")
def services():
    return render_template("services.html")


# ---------- BOOKING (AJAX SUPPORT) ----------
@app.route("/booking", methods=["GET", "POST"])
def booking():
    if request.method == "POST":
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()

                fullname = request.form["fullname"]
                phone = request.form["phone"]
                email = request.form["email"]
                service = request.form["service"]
                date = request.form["date"]

                cursor.execute("""
                    INSERT INTO bookings
                    (fullname, phone, email, service, date)
                    VALUES (%s,%s,%s,%s,%s)
                """, (fullname, phone, email, service, date))

                conn.commit()

                return jsonify({
                    "status": "success",
                    "message": "Your booking has been submitted successfully!"
                })

            except Exception as e:
                print("Booking insert failed:", e)
                return jsonify({"status": "error"})
            finally:
                cursor.close()
                conn.close()

    return render_template("booking.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


# ---------- SALES ----------
@app.route("/sales")
def sales():
    conn = get_db_connection()
    products = []

    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM products")
            products = cursor.fetchall()
        except Exception as e:
            print("Fetching products failed:", e)
        finally:
            cursor.close()
            conn.close()

    return render_template("sales.html", products=products)


# ---------- BUY PRODUCT ----------
@app.route("/buy/<int:product_id>", methods=["GET", "POST"])
def buy_product(product_id):
    conn = get_db_connection()
    product = None

    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM products WHERE id=%s", (product_id,))
            product = cursor.fetchone()

            if request.method == "POST" and product:
                order = {
                    "product_id": product["id"],
                    "product_name": product["name"],
                    "price": product["price"],
                    "customer_name": request.form["name"],
                    "customer_email": request.form["email"],
                    "customer_phone": request.form["phone"],
                    "customer_address": request.form["address"]
                }

                cursor.execute("""
                    INSERT INTO orders
                    (product_id, product_name, price,
                     customer_name, customer_email,
                     customer_phone, customer_address, status)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,'Pending')
                """, (
                    order["product_id"],
                    order["product_name"],
                    order["price"],
                    order["customer_name"],
                    order["customer_email"],
                    order["customer_phone"],
                    order["customer_address"]
                ))

                conn.commit()

                send_customer_email(order["customer_email"],
                                    order["customer_name"],
                                    order["product_name"])

                send_admin_email(order)

                flash("Order placed successfully!", "success")
                return redirect(url_for("order_success"))

        except Exception as e:
            print("Buy product failed:", e)
        finally:
            cursor.close()
            conn.close()

    return render_template("buy.html", product=product)


@app.route("/order-success")
def order_success():
    return render_template("order_success.html")


# ---------- ADMIN LOGIN ----------
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if (request.form["username"] == ADMIN_USERNAME and
                request.form["password"] == ADMIN_PASSWORD):
            session["admin_logged_in"] = True
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Invalid credentials", "danger")

    return render_template("admin_login.html")


# ---------- ADMIN DASHBOARD ----------
@app.route("/admin/dashboard")
def admin_dashboard():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    bookings = []
    orders = []

    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)

            cursor.execute("SELECT * FROM bookings ORDER BY id DESC")
            bookings = cursor.fetchall()

            cursor.execute("SELECT * FROM orders ORDER BY id DESC")
            orders = cursor.fetchall()

        except Exception as e:
            print("Admin dashboard fetch failed:", e)
        finally:
            cursor.close()
            conn.close()

    return render_template("admin_dashboard.html",
                           bookings=bookings,
                           orders=orders)


# ---------- UPDATE ORDER STATUS ----------
@app.route("/admin/order-status/<int:order_id>", methods=["POST"])
def update_order_status(order_id):
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE orders SET status='Done' WHERE id=%s",
                (order_id,))
            conn.commit()
        except Exception as e:
            print("Update order status failed:", e)
        finally:
            cursor.close()
            conn.close()

    return redirect(url_for("admin_dashboard"))


# ---------- ADMIN LOGOUT ----------
@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login"))


# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True)
    
