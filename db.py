import psycopg2

def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="ai_sales_db",
        user="postgres",
        password="Lawrence@1221",
        port="5432"
    )

