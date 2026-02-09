from flask import Flask, render_template, request, redirect, session
import os, json
import firebase_admin
from firebase_admin import credentials, firestore

# ---------------- APP INIT ----------------
app = Flask(__name__)
app.secret_key = "student_records_secret"

# ---------------- FIREBASE INIT ----------------
firebase_key = os.environ.get("FIREBASE_KEY")

cred = credentials.Certificate(json.loads(firebase_key))
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()

# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == "admin" and request.form["password"] == "admin123":
            session["user"] = "admin"
            return redirect("/dashboard")
        return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

# ---------------- DASHBOARD (SAFE) ----------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")

    students = []
    names = []
    percentages = []

    docs = db.collection("students").stream()

    for d in docs:
        data = d.to_dict()

        if "percentage" not in data:
            continue

        students.append(data)
        names.append(data.get("name", "Unknown"))
        percentages.append(data.get("percentage", 0))

    # Sort safely in Python
    students.sort(key=lambda x: x["percentage"], reverse=True)

    return render_template(
        "index.html",
        students=students,
        names=names,
        percentages=percentages
    )

# ---------------- ADD STUDENT ----------------
@app.route("/add", methods=["GET", "POST"])
def add():
    if "user" not in session:
        return redirect("/")

    if request.method == "POST":
        name = request.form["name"]
        roll = request.form["roll"]

        subjects = []
        total = 0
        i = 1

        while f"subject{i}" in request.form:
            subject = request.form[f"subject{i}"]
            marks = int(request.form[f"marks{i}"])
            subjects.append({"name": subject, "marks": marks})
            total += marks
            i += 1

        percentage = total / len(subjects)

        if percentage >= 90:
            grade = "A+"
        elif percentage >= 75:
            grade = "A"
        elif percentage >= 60:
            grade = "B"
        elif percentage >= 40:
            grade = "C"
        else:
            grade = "Fail"

        db.collection("students").add({
            "name": name,
            "roll": roll,
            "subjects": subjects,
            "total": total,
            "percentage": percentage,
            "grade": grade
        })

        return redirect("/dashboard")

    return render_template("add.html")

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ---------------- RUN ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
