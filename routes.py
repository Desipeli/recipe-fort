from app import app
from flask import redirect, render_template, request, session
import meal_categories
from datetime import datetime, date
from werkzeug.security import check_password_hash, generate_password_hash
import users, recipes, comments, likes

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
    users.logout()
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


@app.route("/recipe/<string:recipe_id>")
def recipe(recipe_id):
    result = recipes.recipe(recipe_id)
    comms = comments.get_comments_for_recipe(recipe_id)
    current_like_status = ""
    likes_and_hates = ""
    current_like_status = likes.check_current_status(recipe_id)
    likes_and_hates = likes.likes_and_hates(recipe_id)
    return render_template("recipe.html", likes_and_hates=likes_and_hates, current_like_status=current_like_status, comments=comms, recipe_id=recipe_id, recipe_name=result[0], ingredients=result[1], instructions=result[2], meal_type=result[3], difficulty=result[4], active_time=result[5], passive_time=result[6], time_of_creation=result[7].date(), creator=result[8])

@app.route("/recipe_search", methods=["POST", "GET"])
def recipe_search():
    if request.method == "GET":
        result = recipes.recipe_search_GET()
        return render_template("recipe_list.html", page_header="Recipes", direction="/recipe/", list=result, meal_types=meal_categories.meal_types)
    recipe_name = request.form["recipe_name"]
    username = request.form["username"]
    active_time = request.form["active_time"]
    passive_time = request.form["passive_time"]
    order_name = request.form["order_name"]
    difficulty = request.form['difficulty']
    meal_type = request.form['meal_type']
    result = recipes.recipe_search_POST(recipe_name, username, active_time, passive_time, order_name, difficulty, meal_type)
    return render_template("recipe_list.html", direction="/recipe/", list=result, meal_types=meal_categories.meal_types)

@app.route("/recipe_search/<string:uname>")
def recipe_search_user(uname):
    result = recipes.recipe_search_user(uname)
    return render_template("recipe_list.html", direction="/recipe/", list=result, meal_types=meal_categories.meal_types)

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
    error = recipes.check_recipe(recipe_name, active_time, passive_time, ingredients, amounts, units, instructions, difficulty, meal_type)
    if error:
        return render_template("write_recipe.html", meal_types=meal_categories.meal_types, recipe_name_error=error[0], active_time_error=error[1], passive_time_error=error[2], ingredient_error=error[3], amount_error=error[4], unit_error=error[5], instructions_error=error[6], difficulty_error=error[7], meal_type_error=error[8], ingredient_list=ingredients, amount_list=amounts, unit_list=units)
    if recipes.create_recipe(recipe_name, active_time, passive_time, ingredients, amounts, units, instructions, difficulty, meal_type):
        return redirect("/")
    else:
        return render_template("write_recipe.html", meal_types=meal_categories.meal_types, recipe_name_error="DATABASE ERROR IN RECIPE CREATION", active_time_error=error[1], passive_time_error=error[2], ingredient_error=error[3], amount_error=error[4], unit_error=error[5], instructions_error=error[6], difficulty_error=error[7], meal_type_error=error[8], ingredient_list=ingredients, amount_list=amounts, unit_list=units)

@app.route("/add_ingredient", methods=["POST"])
def add_ingredient():
    ingredients = request.form.getlist('ingredient')
    amounts = request.form.getlist('amount')
    units = request.form.getlist('unit')
    ingredients, amounts, units = recipes.add_ingredient(ingredients, amounts, units)
    return render_template("write_recipe.html", meal_types=meal_categories.meal_types, ingredient_list=ingredients, amount_list=amounts, unit_list=units)

@app.route("/remove_ingredient", methods=["POST"])
def remove_ingredient():
    ingredients = request.form.getlist('ingredient')
    amounts = request.form.getlist('amount')
    units = request.form.getlist('unit')
    ingredients, amounts, units = recipes.remove_ingredient(ingredients, amounts, units)
    return render_template("write_recipe.html", meal_types=meal_categories.meal_types, ingredient_list=ingredients, amount_list=amounts, unit_list=units)

@app.route("/post_comment_to_recipe/<string:recipe_id>", methods=["POST"])
def post_comment_to_recipe(recipe_id):
    comment = request.form['new_comment']
    user_id = users.get_user_id_from_name(session["username"])
    comments.post_comment_to_recipe(user_id, recipe_id, comment)
    return redirect(request.referrer)

@app.route("/delete_comment_from_recipe/<string:comment_id>", methods=["POST"])
def delete_comment_from_recipe(comment_id):
    comments.delete_comment_from_recipe(comment_id)
    return redirect(request.referrer)

@app.route("/like_recipe/<string:recipe_id>", methods=["POST"])
def like_recipe(recipe_id):
    likes.like_recipe(recipe_id)
    return redirect(request.referrer)

@app.route("/hate_recipe/<string:recipe_id>", methods=["POST"])
def hate_recipe(recipe_id):
    likes.hate_recipe(recipe_id)
    return redirect(request.referrer)