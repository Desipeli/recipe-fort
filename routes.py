from app import app
from app import db
from flask import redirect, render_template, request, session
import string

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

@app.route("/create_account")
def create_account():
    return render_template("create_account.html", page_header="Recipe Fort")

@app.route("/register_user", methods=["POST"])
def register_user():
    username = request.form["username"]
    p1 = request.form["newpassword"]
    p2 = request.form["newpassword2"]
    creation_error=""
    if len(username) > 20:
        creation_error = "Username must not be over 20 charaters long."
        return render_template("create_account.html", creation_error=creation_error)
    elif len(p1) > 20:
        creation_error = "Password must not be over 20 charaters long."
        return render_template("create_account.html", creation_error=creation_error)
    elif p1 != p2:
        creation_error = "Passwords did not match"
        return render_template("create_account.html", creation_error=creation_error)

    for letter in username:
        if letter not in string.ascii_letters and letter not in string.digits:
            creation_error = "Use only uppercase and lowercase letters and numbers in username"
            return render_template("create_account.html", creation_error=creation_error)
    
    for letter in p1:
        if letter not in string.ascii_letters and letter not in string.digits:
            creation_error = "Use only uppercase and lowercase letters and numbers in password"
            return render_template("create_account.html", creation_error=creation_error)

    sql = "SELECT username FROM Users WHERE username=:uname"
    result = db.session.execute(sql, {"uname":username}).fetchone()
    if result is not None:
        creation_error = "User with that name already exists"
        return render_template("create_account.html", creation_error=creation_error)

    # No errors, create user
    sql = "INSERT INTO Users (username, password, admin) VALUES (:uname, :pwrd, FALSE)"
    db.session.execute(sql, {"uname":username, "pwrd":p1})
    db.session.commit()
    return render_template("register_user.html", page_header="Recipe Fort")
    
@app.route("/recipes", method=["POST"])
def recipes():
    recipe_name = request.form["recipe_name"]
    if len(recipe_name) > 0:
        sql = "SELECT name FROM Recipes WHERE name LIKE:r_name"
        result = db.session.execute(sql, {"r_name":recipe_name})
        return render_template("recipes_list.html", page_header="Recipes", list=result, direction="/")
    else:
        return render_template("recipes_list.html", page_header="Recipes", list="", direction="/")

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
