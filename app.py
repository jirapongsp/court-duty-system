from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)
DB_NAME = "database.db"


def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    db = get_db()

    db.execute("""
    CREATE TABLE IF NOT EXISTS officers(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        position TEXT
    )
    """)

    db.execute("""
    CREATE TABLE IF NOT EXISTS duties(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        officer_id INTEGER,
        duty_type TEXT,
        duty_date TEXT,
        amount REAL,
        note TEXT
    )
    """)

    db.commit()


@app.route("/")
def index():

    db = get_db()

    duties = db.execute("""
    SELECT duties.*, officers.name
    FROM duties
    LEFT JOIN officers ON duties.officer_id = officers.id
    ORDER BY duty_date DESC
    """).fetchall()

    officers = db.execute("SELECT * FROM officers").fetchall()

    return render_template("index.html", duties=duties, officers=officers)


@app.route("/add_officer", methods=["POST"])
def add_officer():

    name = request.form["name"]
    position = request.form["position"]

    db = get_db()
    db.execute(
        "INSERT INTO officers(name,position) VALUES (?,?)",
        (name, position)
    )
    db.commit()

    return redirect(url_for("index"))


@app.route("/add_duty", methods=["POST"])
def add_duty():

    officer_id = request.form["officer_id"]
    duty_type = request.form["duty_type"]
    duty_date = request.form["duty_date"]
    amount = request.form["amount"]
    note = request.form["note"]

    db = get_db()

    db.execute(
        "INSERT INTO duties(officer_id,duty_type,duty_date,amount,note) VALUES (?,?,?,?,?)",
        (officer_id, duty_type, duty_date, amount, note)
    )

    db.commit()

    return redirect(url_for("index"))


@app.route("/report")
def report():

    month = request.args.get("month")
    year = request.args.get("year")

    db = get_db()

    data = []

    if month and year:

        data = db.execute("""

        SELECT officers.name,
        COUNT(duties.id) as total_duty,
        SUM(duties.amount) as total_amount

        FROM duties
        LEFT JOIN officers ON duties.officer_id = officers.id

        WHERE strftime('%m', duty_date)=?
        AND strftime('%Y', duty_date)=?

        GROUP BY officers.name

        """, (month, year)).fetchall()

    return render_template("report.html", data=data)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
