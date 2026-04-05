from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import mysql.connector
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# ---------- ENV VARIABLES ----------
DB_HOST = os.getenv("MYSQLHOST")
DB_USER = os.getenv("MYSQLUSER")
DB_PASSWORD = os.getenv("MYSQLPASSWORD")
DB_NAME = os.getenv("MYSQLDATABASE")
DB_PORT = os.getenv("MYSQLPORT")

# ---------- FLASK ----------
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback_secret")

# ---------- DATABASE CONNECTION ----------
def get_db_connection():
    try:
        print("DB HOST:", DB_HOST)

        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=int(DB_PORT) if DB_PORT else 3306
        )

        print("Database connected successfully")
        return conn

    except Exception as e:
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
        msg["Subject"] = "Order Confirmation"

        body = f"""
Hello {name},

Your order has been placed successfully.

Product: {product}

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
        msg["Subject"] = "New Order"

        body = f"""
New Order:

Product: {order['product_name']}
Customer: {order['customer_name']}
Phone: {order['customer_phone']}
Email: {order['customer_email']}
"""
        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(ADMIN_EMAIL, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()

    except Exception as e:
        print("Admin email failed:", e)


# ---------- ROUTES ----------

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/booking", methods=["GET", "POST"])
def booking():
    if request.method == "POST":

        conn = get_db_connection()

        if not conn:
            return jsonify({"status": "error", "message": "DB failed"}), 500

        try:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO bookings (fullname, phone, email, service, date)
                VALUES (%s,%s,%s,%s,%s)
            """, (
                request.form.get("fullname"),
                request.form.get("phone"),
                request.form.get("email"),
                request.form.get("service"),
                request.form.get("date")
            ))

            conn.commit()

            return jsonify({"status": "success"})

        except Exception as e:
            print("Booking error:", e)
            return jsonify({"status": "error"}), 500

        finally:
            cursor.close()
            conn.close()

    return render_template("booking.html")


# ---------- RUN ----------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
