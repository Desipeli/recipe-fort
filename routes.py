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

@app.route("/users")
def users():
    result = db.session.execute("SELECT username FROM Users ORDER BY username").fetchall()
    return render_template("linklist.html", page_header="Users", list=result, direction="/users/")

@app.route("/users/<string:name>")
def user_info(name):
    sql = "SELECT R.name FROM Recipes R, Users U WHERE U.id=R.user_id AND U.username=:uname"
    result = db.session.execute(sql, {"uname":name}).fetchall()
    return render_template("linklist.html", page_header=name, list=result, direction="/users/"+name+"/")

@app.route("/users/<string:name>/<string:recipe>")
def recipe(name, recipe):
    sql = "SELECT I.name, I.amount, Ins.text FROM Instructions Ins, Ingredients I, Recipes R, Users U WHERE U.username=:uname AND R.name=:rname AND I.recipe_id=R.id AND R.user_id=U.id AND Ins.recipe_id=R.id"
    result = db.session.execute(sql, {"uname":name, "rname":recipe}).fetchall()
    return render_template("recipe.html", recipe_name=recipe, page_header="Ingredients", ingredients=result, instructions=result)
