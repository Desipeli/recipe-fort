from app import app
from app import db
from flask import redirect, render_template, request, session
from sqlalchemy import asc, desc, true
import string
import math

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "GET":
        return render_template("index.html")
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
    if login_error:
        return render_template("index.html", page_header="Recipe Fort", login_error=login_error)
    return redirect(request.referrer)

@app.route("/logout")
def logout():
    del session["username"]
    return redirect(request.referrer)

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
    


@app.route("/users")
def users():
    result = db.session.execute("SELECT username FROM Users ORDER BY username").fetchall()
    return render_template("linklist.html", page_header="Users", list=result, direction="/users/")

@app.route("/users/<string:name>")
def user_info(name):
    sql = "SELECT R.name FROM Recipes R, Users U WHERE U.id=R.user_id AND U.username=:uname"
    result = db.session.execute(sql, {"uname":name}).fetchall()
    return render_template("linklist.html", page_header=name, list=result, direction="/users/"+name+"/")

#@app.route("/users/<string:name>/<string:recipe>")
#def recipe(name, recipe):
#    sql = "SELECT I.name, I.amount, Ins.text FROM Instructions Ins, Ingredients I, Recipes R, Users U WHERE U.username=:uname AND R.name=:rname AND I.recipe_id=R.id AND R.user_id=U.id AND Ins.recipe_id=R.id"
#    result = db.session.execute(sql, {"uname":name, "rname":recipe}).fetchall()
#    return render_template("recipe.html", recipe_name=recipe, page_header="Ingredients", ingredients=result, instructions=result)

@app.route("/recipe/<string:recipe_id>")
def recipe(recipe_id):
    sql = "SELECT I.name, I.amount, R.name FROM  Ingredients I, Recipes R WHERE R.id=:recipe_id AND I.recipe_id=:recipe_id"
    result = db.session.execute(sql, {"recipe_id":recipe_id}).fetchall()
    sql = "SELECT I.text FROM Instructions I WHERE recipe_id=:recipe_id"
    instructions = db.session.execute(sql, {"recipe_id":recipe_id}).fetchone()
    if instructions == None:
        instructions = ["Missing instructions"]
    print("ins", instructions)
    print("res", result)
    return render_template("recipe.html", recipe_name=result[0][2], page_header="Ingredients", ingredients=result, instructions=instructions[0])


@app.route("/recipe_search", methods=["POST", "GET"])
def recipe_search():
    if request.method == "GET":
        sql = "SELECT id, name FROM Recipes"
        result = db.session.execute(sql).fetchall()
        return render_template("recipe_list.html", page_header="Recipes", direction="/recipe/", list=result)
    recipe_name = request.form["recipe_name"]
    username = request.form["username"]
    active_time = request.form["active_time"]
    passive_time = request.form["passive_time"]
    order_name = request.form["order_name"]


    # Check if int and if times are empty = no limit
    try:
        int(active_time)
    except:
        if active_time == "":
            active_time = math.inf
    try:
        int(passive_time)
    except:
        if passive_time == "":
            passive_time = math.inf

    sql_user = "(SELECT username FROM Users WHERE username LIKE :username)"
    if order_name == "1":
        sql = "SELECT R.id, R.name, U.username FROM Recipes R, Users U WHERE R.name LIKE :r_name AND U.username LIKE :username AND U.id = R.user_id AND R.active_time<=:active_time AND R.passive_time<=:passive_time ORDER BY R.name DESC"
    else:
        sql = "SELECT R.id, R.name, U.username FROM Recipes R, Users U WHERE R.name LIKE :r_name AND U.username LIKE :username AND U.id = R.user_id AND R.active_time<=:active_time AND R.passive_time<=:passive_time ORDER BY R.name ASC"
    result = db.session.execute(sql, {"r_name":"%"+recipe_name+"%", "active_time":active_time, "passive_time":passive_time, "username":"%"+username+"%"}).fetchall()
    return render_template("recipe_list.html", page_heade="Recipes", direction="/recipe/", list=result)

@app.route("/profile/<string:uname>")
def profile(uname):
    if session['username'] == uname:
        return render_template("profile.html", profile_name=uname)
    else:
        return render_template("index.html", login_error=f"You must be logged in as {uname}")

@app.route("/write_recipe")
def write_recipe():
    return render_template("write_recipe.html")

@app.route("/create_recipe", methods=["POST"])
def create_recipe():
    recipe_name=request.form['recipe_name']
    active_time=request.form['active_time']
    passive_time=request.form['passive_time']
    ingredients = request.form.getlist('ingredient')
    amounts = request.form.getlist('amount')
    units = request.form.getlist('unit')
    instructions = request.form['instructions']
    recipe_name_error = ""
    active_time_error = ""
    passive_time_error = ""
    ingredient_error = ""
    amount_error = ""
    unit_error = ""
    instructions_error = ""
    error = False

    if len(recipe_name) == 0 or len(recipe_name) > 100:
        error = True
        recipe_name_error = "Recipe name must be 1-100 characters long"
    try:
        int(active_time)
    except:
        error = True
        active_time_error = "Time must be integer"
    try:
        int(passive_time)
    except:
        error = True
        passive_time_error = "Time must be integer"
    
    for i in ingredients:
        if len(i) == 0 or len(i) > 100:
            error = True
            ingredient_error = "ingredients must be 1-100 characters long"
    for a in amounts:
        try:
            float(a)
        except:
            error = True
            amount_error = "Amount must be a number"
    for u in units:
        if len(u) > 100:
            error = True
            unit_error = "Units must be 0-100 characters long"
    if len(instructions) > 10000:
        error = True
        instructions_error = "Instructions must be <= 10000 characters long"
    if error:
        return render_template("write_recipe.html", recipe_name_error=recipe_name_error, active_time_error=active_time_error, passive_time_error=passive_time_error, ingredient_error=ingredient_error, amount_error=amount_error, unit_error=unit_error, instructions_error=instructions_error, ingredient_list=ingredients, amount_list=amounts, unit_list=units)
    print("Recipe name:", recipe_name)
    print("active time:", active_time)
    print("passive time:", passive_time)
    for i in range(len(ingredients)):
        print(ingredients[i], amounts[i], units[i])
    print("instructions:")
    print(instructions)

@app.route("/add_ingredient", methods=["POST"])
def add_ingredient():
    ingredients = request.form.getlist('ingredient')
    amounts = request.form.getlist('amount')
    units = request.form.getlist('unit')
    print(ingredients, amounts, units)
    if ingredients == None:
        ingredients = []
        units = []
        amounts = []
    ingredients.append(" ")
    amounts.append(0)
    units.append(" ")
    return render_template("write_recipe.html", ingredient_list=ingredients, amount_list=amounts, unit_list=units)

@app.route("/remove_ingredient", methods=["POST"])
def remove_ingredient():
    ingredients = request.form.getlist('ingredient')
    amounts = request.form.getlist('amount')
    units = request.form.getlist('unit')
    if len(ingredients) > 0:
        ingredients.pop()
        amounts.pop()
        units.pop()
    return render_template("write_recipe.html", ingredient_list=ingredients, amount_list=amounts, unit_list=units)