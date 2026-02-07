import pandas as pd
import psycopg2

# Reading CSV
df = pd.read_csv(r"C:\AI SQL assistant pro\data\sales_data_sample.csv", encoding="latin1")

print("Rows in CSV:", len(df))

# Connecting to PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    database="ai_sales_db",
    user="postgres",
    password="Lawrence@1221",
    port="5432"
)

cur = conn.cursor()

# Inserting row by row
for _, row in df.iterrows():
    cur.execute("""
        INSERT INTO sales VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, tuple(row))

conn.commit()
conn.close()

print("DATA IMPORTED SUCCESSFULLY")
