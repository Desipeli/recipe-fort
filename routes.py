from app import app
from db import db
from flask import redirect, render_template, request, session
import string
import math
import meal_categories
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
import users

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "GET":
        return render_template("index.html")
    username = request.form["username"]
    password = request.form["password"]
    if users.login(username, password):
        return redirect(request.referrer)
    return render_template("index.html", page_header="Recipe Fort", login_error="Wrong username or password")

@app.route("/logout")
def logout():
    return redirect(request.referrer)

@app.route("/create_account")
def create_account():
    return render_template("create_account.html")

@app.route("/register_user", methods=["POST"])
def register_user():
    username = request.form["username"]
    p1 = request.form["newpassword"]
    p2 = request.form["newpassword2"]
    creation_error = ""
    username_error = users.check_username_valid(username)
    password_error = users.check_password_valid(p1, p2)

    if username_error: creation_error = username_error + ". "
    if password_error: creation_error += password_error
    if creation_error:
        return render_template("create_account.html", creation_error=creation_error)

    if users.check_if_user_exists(username):
        creation_error = "User with that name already exists"
        return render_template("create_account.html", creation_error=creation_error)

    # No errors, create user
    creation_message_1 = f"Account {username} created successfully. Go back to "
    creation_message_2 = " to log in"
    if users.register_user(username, p1) == False:
        creation_message_1 = f"An error occurred during registration, try again later: "
        creation_message_2 = ""
    return render_template("register_user.html", creation_message_1=creation_message_1, creation_message_2=creation_message_2)
    

#@app.route("/users/<string:name>")
#def user_info(name):
#    sql = "SELECT R.name FROM Recipes R, Users U WHERE U.id=R.user_id AND U.username=:uname"
#    result = db.session.execute(sql, {"uname":name}).fetchall()
#    return render_template("linklist.html", page_header=name, list=result, direction="/users/"+name+"/")

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
        sql = "SELECT R.id, R.name, U.username FROM Recipes R, Users U WHERE R.user_id=U.id"
        result = db.session.execute(sql).fetchall()
        return render_template("recipe_list.html", page_header="Recipes", direction="/recipe/", list=result, meal_types=meal_categories.meal_types)
    recipe_name = request.form["recipe_name"]
    username = request.form["username"]
    active_time = request.form["active_time"]
    passive_time = request.form["passive_time"]
    order_name = request.form["order_name"]
    difficulty = request.form['difficulty']
    if difficulty == "": difficulty = 0
    meal_type = request.form['meal_type']
    meal_type_column = "meal_type"

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
    sql = "SELECT R.id, R.name, U.username FROM Recipes R, Users U WHERE R.name LIKE :r_name AND U.username LIKE :username AND U.id = R.user_id AND R.active_time<=:active_time AND R.passive_time<=:passive_time AND difficulty<=:difficulty"
    if meal_type in meal_categories.meal_types:
        sql += " AND meal_type=:meal_type"
    if order_name == "0":
        sql += " ORDER BY R.name ASC"
    elif order_name == "1":
        sql += " ORDER BY R.name DESC"
    elif order_name == "2":
        sql += " ORDER BY R.timestamp DESC"
    elif order_name == "3":
        sql += " ORDER BY R.timestamp ASC"
    result = db.session.execute(sql, {"r_name":"%"+recipe_name+"%", "active_time":active_time, "passive_time":passive_time, "username":"%"+username+"%", "difficulty":difficulty, "meal_type":meal_type}).fetchall()
    return render_template("recipe_list.html", page_heade="Recipes", direction="/recipe/", list=result, meal_types=meal_categories.meal_types)

@app.route("/profile/<string:uname>")
def profile(uname):
    if session['username'] == uname:
        return render_template("profile.html", profile_name=uname)
    else:
        return render_template("index.html", login_error=f"You must be logged in as {uname}")

@app.route("/write_recipe")
def write_recipe():
    return render_template("write_recipe.html", meal_types=meal_categories.meal_types)

@app.route("/check_recipe", methods=["POST"])
def check_recipe():
    meal_types = meal_categories.meal_types
    recipe_name=request.form['recipe_name']
    active_time=request.form['active_time']
    passive_time=request.form['passive_time']
    ingredients = request.form.getlist('ingredient')
    amounts = request.form.getlist('amount')
    units = request.form.getlist('unit')
    instructions = request.form['instructions']
    difficulty = request.form['difficulty']
    meal_type = request.form['meal_type']
    difficulty_error = ""
    meal_type_error = ""
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
    try:
        int(difficulty)
    except:
        error = True
        difficulty_error = "Difficulty must be set 0-3"
    if meal_type not in meal_types:
        error = True
        meal_type_error = "Select correct category"
    
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
        return render_template("write_recipe.html", meal_types=meal_categories.meal_types, recipe_name_error=recipe_name_error, active_time_error=active_time_error, passive_time_error=passive_time_error, ingredient_error=ingredient_error, amount_error=amount_error, unit_error=unit_error, difficulty_error=difficulty_error, instructions_error=instructions_error, ingredient_list=ingredients, amount_list=amounts, unit_list=units)
    sql_user_id = "SELECT id FROM Users WHERE username =:uname"
    user_id = db.session.execute(sql_user_id, {"uname":session["username"]}).fetchone()[0]
    dt = datetime.now()
    sql_create_recipe = "INSERT INTO Recipes (name, user_id, difficulty, active_time, passive_time, meal_type, timestamp) VALUES (:recipe_name, :user_id, :difficulty, :active_time, :passive_time, :meal_type, :timestamp)"
    db.session.execute(sql_create_recipe, {"recipe_name":recipe_name, "user_id":user_id, "difficulty":difficulty, "active_time":active_time, "passive_time":passive_time, "meal_type":meal_type, "timestamp":dt})
    db.session.commit()
    sql_recipe_id = "SELECT id FROM Recipes WHERE name=:recipe_name AND user_id=:user_id AND timestamp=:timestamp"
    recipe_id = db.session.execute(sql_recipe_id, {"recipe_name":recipe_name, "user_id":user_id, "timestamp":dt}).fetchone()[0]
    for i in range(len(ingredients)):
        i_name = ingredients[i]
        i_amount = str(amounts[i]) + " "  + units[i]
        sql_insert_ingredients = "INSERT INTO Ingredients (recipe_id, name, amount) VALUES (:recipe_id, :name, :amount)"
        db.session.execute(sql_insert_ingredients, {"recipe_id":recipe_id, "name":i_name, "amount":i_amount})
    sql_instructions = "INSERT INTO Instructions (recipe_id, text) VALUES (:recipe_id, :text)"
    db.session.execute(sql_instructions, {"recipe_id":recipe_id, "text":instructions})
    db.session.commit()
    return redirect("/")

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
    return render_template("write_recipe.html", meal_types=meal_categories.meal_types, ingredient_list=ingredients, amount_list=amounts, unit_list=units)

@app.route("/remove_ingredient", methods=["POST"])
def remove_ingredient():
    ingredients = request.form.getlist('ingredient')
    amounts = request.form.getlist('amount')
    units = request.form.getlist('unit')
    if len(ingredients) > 0:
        ingredients.pop()
        amounts.pop()
        units.pop()
    return render_template("write_recipe.html", meal_types=meal_categories.meal_types, ingredient_list=ingredients, amount_list=amounts, unit_list=units)
