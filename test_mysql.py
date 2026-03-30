import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Pratiksha@07",
    database="shree_sai_services"
)

if conn.is_connected():
    print("✅ MySQL Connected Successfully")

conn.close()
