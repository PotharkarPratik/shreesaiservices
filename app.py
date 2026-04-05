from flask import Flask, render_template, request, jsonify
import mysql.connector
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


# ================= ROUTES =================

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/services")
def services():
    return render_template("services.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/sales")
def sales():
    return render_template("sales.html")


# ---------- BOOKING PAGE + API ----------
@app.route("/booking", methods=["GET", "POST"])
def booking():
    if request.method == "POST":

        conn = get_db_connection()

        if not conn:
            return jsonify({"status": "error", "message": "Database failed"}), 500

        try:
            cursor = conn.cursor()

            fullname = request.form.get("fullname")
            phone = request.form.get("phone")
            email = request.form.get("email")
            service = request.form.get("service")
            date = request.form.get("date")

            cursor.execute("""
                INSERT INTO bookings (fullname, phone, email, service, date)
                VALUES (%s,%s,%s,%s,%s)
            """, (fullname, phone, email, service, date))

            conn.commit()

            return jsonify({
                "status": "success",
                "message": "Booking successful"
            })

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
