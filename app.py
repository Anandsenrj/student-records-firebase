from flask import Flask, render_template, request, redirect, session
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

# ✅ 1. CREATE FLASK APP FIRST
app = Flask(__name__)
app.secret_key = "student_records_secret"

# ✅ 2. FIREBASE INIT (ONLY ONCE)
firebase_key = os.environ.get("FIREBASE_KEY")

cred = credentials.Certificate(json.loads(firebase_key))

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()

# ✅ 3. ROUTES (AFTER app IS DEFINED)

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == "admin" and request.form["password"] == "admin123":
            session["user"] = "admin"
            return redirect("/dashboard")
        return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")

    docs = db.collection("students") \
             .order_by("percentage", direction=firestore.Query.DESCENDING) \
             .stream()

    students = []
    names = []
    percentages = []

    for d in docs:
        data = d.to_dict()
        students.append(data)
        names.append(data["name"])
        percentages.append(data["percentage"])

    return render_template(
        "index.html",
        students=students,
        names=names,
        percentages=percentages
    )


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
            sub = request.form[f"subject{i}"]
            marks = int(request.form[f"marks{i}"])
            subjects.append({"name": sub, "marks": marks})
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


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ✅ 4. RUN APP (LAST)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

