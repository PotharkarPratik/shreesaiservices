import os
import mysql.connector

try:
    conn = mysql.connector.connect(
        host=os.getenv("MYSQLHOST"),
        user=os.getenv("MYSQLUSER"),
        password=os.getenv("MYSQLPASSWORD"),
        database=os.getenv("MYSQLDATABASE"),
        port=int(os.getenv("MYSQLPORT", 3306))
    )

    if conn.is_connected():
        print("Database connected successfully")

except Exception as e:
    print("Database connection failed:", e)
