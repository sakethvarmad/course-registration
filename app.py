import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
DB = "courses.db"

COURSES = [
    ("CS101", "Introduction to Programming"),
    ("CS201", "Data Structures"),
    ("CS301", "Database Systems"),
    ("CS401", "Web Application Development"),
]


def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            email TEXT NOT NULL,
            course_code TEXT NOT NULL)""")


@app.route("/", methods=["GET", "POST"])
def register():
    errors = []
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        course = request.form.get("course", "").strip()
        if not name:
            errors.append("Name is required.")
        if "@" not in email or "." not in email:
            errors.append("Enter a valid email.")
        if course not in [c[0] for c in COURSES]:
            errors.append("Please select a valid course.")
        if not errors:
            with get_db() as conn:
                dup = conn.execute("SELECT 1 FROM registrations WHERE email=? AND course_code=?",
                                   (email, course)).fetchone()
                if dup:
                    errors.append("You are already registered for this course.")
                else:
                    conn.execute("INSERT INTO registrations (student_name, email, course_code) VALUES (?, ?, ?)",
                                 (name, email, course))
                    return redirect(url_for("registrations"))
    return render_template("register.html", courses=COURSES, errors=errors)


@app.route("/registrations")
def registrations():
    titles = dict(COURSES)
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM registrations").fetchall()
    return render_template("registrations.html", rows=rows, titles=titles)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
