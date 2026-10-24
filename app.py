
from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    redirect,
    url_for,
    session
)
from database import create_database
from werkzeug.security import check_password_hash
from functools import wraps
from pathlib import Path
import sqlite3
import csv
from io import StringIO
from flask import Response
import os

# Load security settings from .env
env_path = Path(__file__).resolve().parent / ".env"

if env_path.exists():
    for line in env_path.read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())

SECRET_KEY = os.environ.get("SECRET_KEY")
PASSWORD_HASH = os.environ.get("INSTRUCTOR_PASSWORD_HASH")

if not SECRET_KEY or not PASSWORD_HASH:
    raise RuntimeError(
        "Missing security settings. Check your .env file."
    )

app = Flask(__name__)
app.secret_key = SECRET_KEY

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax"
)

DATABASE = str(
    Path(__file__).resolve().parent / "dronelearn.db"
)

create_database()


# Require instructor login
def instructor_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if not session.get("instructor_logged_in"):
            return redirect(url_for("login"))
        return function(*args, **kwargs)
    return wrapper


# Home page
@app.route("/")
def home():
    return render_template("index.html")


# Lessons page
@app.route("/lessons")
def lessons():
    return render_template("lessons.html")


# Student quiz
@app.route("/quiz")
def quiz():
    return render_template("quiz.html")


# Save student quiz results
@app.route("/submit-quiz", methods=["POST"])
def submit_quiz():
    data = request.get_json(silent=True) or {}

    student_name = str(
        data.get("student_name", "")
    ).strip()

    answers = data.get("answers", {})

    if not student_name or len(student_name) > 100:
        return jsonify({
            "error": "Please enter a valid student name."
        }), 400

    if not isinstance(answers, dict):
        return jsonify({
            "error": "Invalid answers."
        }), 400

    correct_answers = {
        "q1": "b",
        "q2": "a",
        "q3": "b",
        "q4": "b",
        "q5": "b"
    }

    if any(
        answers.get(question) not in ("a", "b", "c")
        for question in correct_answers
    ):
        return jsonify({
            "error": "Please answer all five questions."
        }), 400

    score = sum(
        answers[question] == correct
        for question, correct in correct_answers.items()
    )

    connection = sqlite3.connect(DATABASE)

    try:
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO quiz_results
            (student_name, score, total_questions)
            VALUES (?, ?, ?)
        """, (
            student_name,
            score,
            len(correct_answers)
        ))
        connection.commit()
    finally:
        connection.close()

    return jsonify({
        "student_name": student_name,
        "score": score,
        "total": len(correct_answers),
        "percentage": round(
            score / len(correct_answers) * 100
        )
    })


# Instructor login
@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("instructor_logged_in"):
        return redirect(url_for("instructor"))

    error = None

    if request.method == "POST":
        password = request.form.get("password", "")

        if check_password_hash(PASSWORD_HASH, password):
            session.clear()
            session["instructor_logged_in"] = True
            return redirect(url_for("instructor"))

        error = "Incorrect password. Please try again."

    return render_template("login.html", error=error)


# Protected instructor dashboard
@app.route("/instructor")
@instructor_required
def instructor():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT id, student_name, score,
                   total_questions, submitted_at
            FROM quiz_results
            ORDER BY submitted_at DESC, id DESC
        """)
        results = cursor.fetchall()

        cursor.execute("""
            SELECT student_name, lesson_number
            FROM lesson_progress
            ORDER BY student_name COLLATE NOCASE, lesson_number
        """)
        rows = cursor.fetchall()

        students = {}

        for row in rows:
            name = row["student_name"]

            if name not in students:
                students[name] = set()

            students[name].add(row["lesson_number"])

        lesson_progress = []

        for name, completed in students.items():
            count = len(completed)

            lesson_progress.append({
                "student_name": name,
                "completed_lessons": completed,
                "count": count,
                "percentage": round(count / 3 * 100)
            })

    finally:
        connection.close()

    return render_template(
        "instructor.html",
        results=results,
        lesson_progress=lesson_progress
    )


# Instructor logout
@app.route("/logout", methods=["POST"])
@instructor_required
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/complete-lesson", methods=["POST"])
def complete_lesson():
    data = request.get_json(silent=True) or {}

    student_name = str(data.get("student_name", "")).strip()
    lesson_number = data.get("lesson_number")

    if not student_name or len(student_name) > 100:
        return jsonify({"error": "Please enter a valid student name."}), 400

    if lesson_number not in (1, 2, 3):
        return jsonify({"error": "Invalid lesson number."}), 400

    connection = sqlite3.connect(DATABASE)

    try:
        connection.execute(
            """
            INSERT OR IGNORE INTO lesson_progress
            (student_name, lesson_number)
            VALUES (?, ?)
            """,
            (student_name, lesson_number)
        )
        connection.commit()
    finally:
        connection.close()

    return jsonify({
        "success": True,
        "message": f"Lesson {lesson_number} completed!"
    })
@app.route("/export-quiz-results")
@instructor_required
def export_quiz_results():
    connection = sqlite3.connect(DATABASE)

    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT student_name, score, total_questions, submitted_at
            FROM quiz_results
            ORDER BY submitted_at DESC
        """)
        results = cursor.fetchall()
    finally:
        connection.close()

    output = StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "Student Name",
        "Score",
        "Total Questions",
        "Percentage",
        "Submission Date"
    ])

    for name, score, total, date in results:
        percentage = round(score / total * 100) if total else 0
        writer.writerow([
            name, score, total, percentage, date
        ])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=dronelearn_quiz_results.csv"
        }
    )
if __name__ == "__main__":
    app.run(debug=False, port=5002)
