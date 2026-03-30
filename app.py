from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "secret")

# -------- TEMP STORAGE (instead of database) --------
bookings = []
products = [
    {"id": 1, "name": "AC Service", "price": 1500},
    {"id": 2, "name": "Washing Machine Repair", "price": 800}
]
orders = []

# ---------- ROUTES ----------

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/services")
def services():
    return render_template("services.html")

@app.route("/booking", methods=["GET", "POST"])
def booking():
    if request.method == "POST":
        data = {
            "fullname": request.form["fullname"],
            "phone": request.form["phone"],
            "email": request.form["email"],
            "service": request.form["service"],
            "date": request.form["date"]
        }
        bookings.append(data)
        return jsonify({"status": "success"})
    return render_template("booking.html")

@app.route("/sales")
def sales():
    return render_template("sales.html", products=products)

@app.route("/buy/<int:product_id>", methods=["GET", "POST"])
def buy_product(product_id):
    product = next((p for p in products if p["id"] == product_id), None)

    if request.method == "POST" and product:
        order = {
            "product": product["name"],
            "name": request.form["name"],
            "email": request.form["email"],
            "phone": request.form["phone"],
            "address": request.form["address"]
        }
        orders.append(order)
        return redirect(url_for("order_success"))

    return render_template("buy.html", product=product)

@app.route("/order-success")
def order_success():
    return render_template("order_success.html")

if __name__ == "__main__":
    app.run()
