from app import app
from app import db
from flask import redirect, render_template, request, session, flash

@app.route("/")
def index():
    return render_template("index.html", page_header="Recipe Fort")

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    sql = "SELECT password FROM Users WHERE username=:uname"
    result = db.session.execute(sql, {"uname":username})
    fetched_pw = result.fetchone()
    login_error = "Wrong username or password"
    if fetched_pw:
        if fetched_pw.password == password:
            session["username"] = username
            login_error = ""
    return render_template("index.html", page_header="Recipe Fort", login_error=login_error)

@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")
