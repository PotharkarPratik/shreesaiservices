import mysql.connector

conn = mysql.connector.connect(
    host="127.0.0.1",   # ✅ FIXED
    user="root",
    password="Pratiksha@07",
    database="shree_sai_services"
)

if conn.is_connected():
    print("✅ MySQL Connected Successfully")

conn.close()