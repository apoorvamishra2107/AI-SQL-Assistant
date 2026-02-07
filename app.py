from flask import Flask, render_template, request, redirect, session
import pandas as pd
import psycopg2
from flask_bcrypt import Bcrypt
import plotly.express as px
import ollama

app = Flask(__name__)
app.secret_key = "secret123"
bcrypt = Bcrypt(app)

# DATABASE CONNECTION
def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="ai_sales_db",
        user="postgres",
        password="Lawrence@1221",
        port="5432"
    )

# LOCAL AI → SQL GENERATOR
def generate_sql(question):
    prompt = f"""
You are an expert PostgreSQL developer.

IMPORTANT RULES:
- Use PostgreSQL syntax ONLY
- DO NOT use backticks (`) ever
- DO NOT use MySQL syntax
- Return ONLY SQL query
- No explanation
- No markdown

Table name: sales

Columns:
ordernumber
quantityordered
priceeach
orderlinenumber
sales
orderdate
status
productline
msrp
productcode
customername
phone
addressline1
city
state
postalcode
country
territory
contactlastname
contactfirstname
dealsize

Question: {question}
SQL:
"""

    response = ollama.chat(
        model="mistral",
        messages=[{"role": "user", "content": prompt}]
    )

    sql = response["message"]["content"].strip()
    sql = sql.replace("```sql", "").replace("```", "").strip()
    sql = sql.replace("`", "")
    return sql

# LOGIN
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["username"]
        pwd = request.form["password"]

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT password FROM users WHERE username=%s", (user,))
        data = cur.fetchone()
        conn.close()

        if data and bcrypt.check_password_hash(data[0], pwd):
            session["user"] = user
            return redirect("/dashboard")

    return render_template("login.html")

# SIGNUP
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        user = request.form["username"]
        pwd = bcrypt.generate_password_hash(
            request.form["password"]
        ).decode("utf-8")

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users(username,password) VALUES(%s,%s)",
            (user, pwd)
        )
        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("signup.html")

# SMART AUTO CHART ENGINE
def generate_chart(df):
    if df.empty:
        return None

    numeric_cols = df.select_dtypes(include=['int64','float64']).columns
    text_cols = df.select_dtypes(include=['object']).columns

    try:
        # Category + Number → Bar chart
        if len(text_cols) >= 1 and len(numeric_cols) >= 1:
            fig = px.bar(
                df,
                x=text_cols[0],
                y=numeric_cols[0],
                title=f"{numeric_cols[0]} by {text_cols[0]}"
            )
            return fig.to_html(full_html=False)

        # Number + Number → Scatter
        if len(numeric_cols) >= 2:
            fig = px.scatter(
                df,
                x=numeric_cols[0],
                y=numeric_cols[1],
                title=f"{numeric_cols[0]} vs {numeric_cols[1]}"
            )
            return fig.to_html(full_html=False)

        return None

    except:
        return None

# DASHBOARD
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    table = None
    chart = None
    sql_query = None

    if request.method == "POST":
        question = request.form["question"]

        try:
            sql_query = generate_sql(question)

            conn = get_connection()
            df = pd.read_sql(sql_query, conn)
            conn.close()

            if df.empty:
                table = "Query executed but returned no data."
            else:
                table = df.to_html(classes="table table-bordered", index=False)
                chart = generate_chart(df)

        except Exception as e:
            table = f"Error: {str(e)}"
            chart = None

    return render_template(
        "dashboard.html",
        table=table,
        chart=chart,
        query=sql_query
    )

# RUN APP
if __name__ == "__main__":
    app.run(debug=True)
