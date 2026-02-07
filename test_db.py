import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",
        database="ai_sales_db",
        user="postgres",
        password="Lawrence@1221"
    )
    print("Connection successful!")
    conn.close()
except Exception as e:
    print("Error:", e)
