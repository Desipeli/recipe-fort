from os import abort
from app import app
from flask import redirect, render_template, request, request_started, session
import meal_categories
import users, recipes, comments, likes

@app.route("/", methods=["GET", "POST"])
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

@app.route("/logout", methods=["POST"])
def logout():
    users.logout()
    return redirect(request.referrer)

@app.route("/create_account", methods=["GET", "POST"])
def create_account():
    if request.method == "GET":
        return render_template("create_account.html")
    else:
        username = request.form["username"]
        p1 = request.form["newpassword"]
        p2 = request.form["newpassword2"]
        login_error = ""
        username_error = users.check_username_valid(username)
        password_error = users.check_password_valid(p1, p2)

        if username_error: login_error = username_error + ". "
        if password_error: login_error += password_error
        if login_error:
            return render_template("create_account.html", login_error=login_error)

        if users.check_if_user_exists(username):
            login_error = "User with that name already exists"
            return render_template("create_account.html", login_error=login_error)

        # No errors, create user
        creation_error = f"Account {username} created successfully!"
        if users.register_user(username, p1) == False:
            login_error = f"An error occurred during registration, try again later: "
            return render_template("create_account.html", creation_error=creation_error)
        else:
            users.login(username, p1)
            return render_template("/create_account.html", creation_error=creation_error)

@app.route("/recipe/<string:recipe_id>")
def recipe(recipe_id):
    result = recipes.recipe(recipe_id)
    comms = comments.get_comments_for_recipe(recipe_id)
    current_like_status = ""
    likes_and_hates = ""
    current_like_status = likes.check_current_status(recipe_id)
    likes_and_hates = likes.likes_and_hates(recipe_id)
    return render_template("recipe.html", likes_and_hates=likes_and_hates, current_like_status=current_like_status, comments=comms, recipe_id=recipe_id, recipe_name=result[0][0], ingredients=result[1], amounts=result[2], units=result[3], instructions=result[4], meal_type=result[0][1], difficulty=result[0][2], active_time=result[0][3], passive_time=result[0][4], time_of_creation=result[0][5].date(), creator=result[5])

@app.route("/edit_recipe", methods=["POST"])
def edit_recipe():
    print("EDIT")
    if request.form["csrf_token"] != session["csrf_token"]:
        abort(403)
    recipe_id = request.form["recipe_id"]
    result = recipes.recipe(recipe_id)
    return render_template("edit_recipe.html", recipe_id=recipe_id, recipe_name=result[0][0], meal_type=result[0][1], instructions=result[4], difficulty=result[0][2], active_time=result[0][3], passive_time=result[0][4] ,ingredient_list=result[1], amount_list=result[2], unit_list=result[3], meal_types=meal_categories.meal_types, recipe_name_error="", active_time_error="", passive_time_error="", ingredient_error="", amount_error="", unit_error="", instructions_error="", difficulty_error="", meal_type_error="")

# If recipe is modified, a new one is created and old removed from db
@app.route("/confirm_edit", methods=["POST"]) 
def confirm_edit():
    if request.form["csrf_token"] != session["csrf_token"]:
        abort(403)
    meal_types = meal_categories.meal_types
    recipe_id = request.form["recipe_id"]
    recipe_name=request.form['recipe_name']
    active_time=request.form['active_time']
    passive_time=request.form['passive_time']
    ingredients = request.form.getlist('ingredient')
    amounts = request.form.getlist('amount')
    units = request.form.getlist('unit')
    instructions = request.form['instructions']
    difficulty = request.form['difficulty']
    meal_type = request.form['meal_type']
    error = recipes.check_recipe(recipe_name, active_time, passive_time, ingredients, amounts, units, instructions, difficulty, meal_type, True)
    if error:
        return render_template("edit_recipe.html", meal_type=meal_type, recipe_id=recipe_id, recipe_name=recipe_name, instructions=instructions, difficulty=difficulty, active_time=active_time, passive_time=passive_time ,ingredient_list=ingredients, amount_list=amounts, unit_list=units, meal_types=meal_categories.meal_types, recipe_name_error=error[0], active_time_error=error[1], passive_time_error=error[2], ingredient_error=error[3], amount_error=error[4], unit_error=error[5], instructions_error=error[6], difficulty_error=error[7], meal_type_error=error[8])
    if recipes.create_recipe(recipe_name, active_time, passive_time, ingredients, amounts, units, instructions, difficulty, meal_type):
        recipes.delete_recipe(recipe_id, users.get_user_id_from_name(session["username"]))
        return redirect("/")


@app.route("/recipe_search", methods=["POST", "GET"])
def recipe_search():
    if request.method == "GET":
        result = recipes.recipe_search_GET()
        return render_template("recipe_list.html", direction="/recipe/", list=result, meal_types=meal_categories.meal_types, order_selected="2")
    recipe_name = request.form["recipe_name"]
    username = request.form["username"]
    active_time = request.form["active_time"]
    passive_time = request.form["passive_time"]
    order_name = request.form["order_name"]
    difficulty = request.form['difficulty']
    meal_type = request.form['meal_type']
    ingredient_list = request.form.getlist('ingredient')
    result = recipes.recipe_search_POST(recipe_name, username, active_time, passive_time, order_name, difficulty, meal_type, ingredient_list)
    return render_template("recipe_list.html", direction="/recipe/", list=result, meal_types=meal_categories.meal_types, ingredient_list=ingredient_list, order_selected=order_name)

@app.route("/recipe_search/<string:uname>")
def recipe_search_user(uname):
    result = recipes.recipe_search_user(uname)
    return render_template("recipe_list.html", direction="/recipe/", list=result, meal_types=meal_categories.meal_types, order_selected="2")

@app.route("/profile/<string:uname>")
def profile(uname):
    if not session.get("username") is None:
        if session['username'] == uname:
            return render_template("profile.html", profile_name=uname)
        else:
            return render_template("profile.html")
    else:
        return render_template("profile.html")

@app.route("/write_recipe")
def write_recipe():
    return render_template("write_recipe.html", meal_types=meal_categories.meal_types, ingredient_list=[""], amount_list=[0], unit_list="")

@app.route("/check_recipe", methods=["POST"])
def check_recipe():
    if request.form["csrf_token"] != session["csrf_token"]:
        abort(403)
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
    error = recipes.check_recipe(recipe_name, active_time, passive_time, ingredients, amounts, units, instructions, difficulty, meal_type, False)
    if error:
        return render_template("write_recipe.html", meal_types=meal_types, recipe_name_error=error[0], active_time_error=error[1], passive_time_error=error[2], ingredient_error=error[3], amount_error=error[4], unit_error=error[5], instructions_error=error[6], difficulty_error=error[7], meal_type_error=error[8], ingredient_list=ingredients, amount_list=amounts, unit_list=units)
    recipe_id = recipes.create_recipe(recipe_name, active_time, passive_time, ingredients, amounts, units, instructions, difficulty, meal_type)
    if recipe_id != False:
        return redirect(f"/recipe/{recipe_id}")
    else:
        return render_template("write_recipe.html", meal_types=meal_types, recipe_name_error="DATABASE ERROR IN RECIPE CREATION", active_time_error=error[1], passive_time_error=error[2], ingredient_error=error[3], amount_error=error[4], unit_error=error[5], instructions_error=error[6], difficulty_error=error[7], meal_type_error=error[8], ingredient_list=ingredients, amount_list=amounts, unit_list=units)

@app.route("/add_ingredient", methods=["POST"])
def add_ingredient():
    if request.form["csrf_token"] != session["csrf_token"]:
        abort(403)
    ingredients = request.form.getlist('ingredient')
    amounts = request.form.getlist('amount')
    units = request.form.getlist('unit')
    ingredients, amounts, units = recipes.add_ingredient(ingredients, amounts, units) 
    return render_template("write_recipe.html", meal_types=meal_categories.meal_types, ingredient_list=ingredients, amount_list=amounts, unit_list=units)

@app.route("/add_ingredient_edited", methods=["POST"])
def add_ingredient_edited():
    if request.form["csrf_token"] != session["csrf_token"]:
        abort(403)
    recipe_id = request.form["recipe_id"]
    recipe_name=request.form['recipe_name']
    active_time=request.form['active_time']
    passive_time=request.form['passive_time']
    ingredients = request.form.getlist('ingredient')
    amounts = request.form.getlist('amount')
    units = request.form.getlist('unit')
    instructions = request.form['instructions']
    difficulty = request.form['difficulty']
    meal_type = request.form['meal_type']
    ingredients = request.form.getlist('ingredient')
    amounts = request.form.getlist('amount')
    units = request.form.getlist('unit')
    ingredients, amounts, units = recipes.add_ingredient(ingredients, amounts, units)
    return render_template("edit_recipe.html", meal_type=meal_type, recipe_id=recipe_id, meal_types=meal_categories.meal_types, ingredient_list=ingredients, amount_list=amounts, unit_list=units, recipe_name=recipe_name, active_time=active_time, passive_time=passive_time, difficulty=difficulty, instructions=instructions)

@app.route("/remove_ingredient", methods=["POST"])
def remove_ingredient():
    if request.form["csrf_token"] != session["csrf_token"]:
        abort(403)
    ingredients = request.form.getlist('ingredient')
    amounts = request.form.getlist('amount')
    units = request.form.getlist('unit')
    ingredients, amounts, units = recipes.remove_ingredient(ingredients, amounts, units)
    return render_template("write_recipe.html", meal_types=meal_categories.meal_types, ingredient_list=ingredients, amount_list=amounts, unit_list=units)

@app.route("/remove_ingredient_edited", methods=["POST"])
def remove_ingredient_edited():
    if request.form["csrf_token"] != session["csrf_token"]:
        abort(403)
    recipe_id = request.form["recipe_id"]
    recipe_name=request.form['recipe_name']
    active_time=request.form['active_time']
    passive_time=request.form['passive_time']
    ingredients = request.form.getlist('ingredient')
    amounts = request.form.getlist('amount')
    units = request.form.getlist('unit')
    instructions = request.form['instructions']
    difficulty = request.form['difficulty']
    meal_type = request.form['meal_type']
    ingredients = request.form.getlist('ingredient')
    amounts = request.form.getlist('amount')
    units = request.form.getlist('unit')
    ingredients, amounts, units = recipes.remove_ingredient(ingredients, amounts, units)
    return render_template("edit_recipe.html", meal_type=meal_type, recipe_id=recipe_id, meal_types=meal_categories.meal_types, ingredient_list=ingredients, amount_list=amounts, unit_list=units, recipe_name=recipe_name, active_time=active_time, passive_time=passive_time, difficulty=difficulty, instructions=instructions)

@app.route("/post_comment_to_recipe/<string:recipe_id>", methods=["POST"])
def post_comment_to_recipe(recipe_id):
    if request.form["csrf_token"] != session["csrf_token"]:
        abort(403)
    comment = request.form['new_comment']
    user_id = users.get_user_id_from_name(session["username"])
    comments.post_comment_to_recipe(user_id, recipe_id, comment)
    return redirect(request.referrer)

@app.route("/delete_comment_from_recipe/<string:comment_id>", methods=["POST"])
def delete_comment_from_recipe(comment_id):
    if request.form["csrf_token"] != session["csrf_token"]:
        abort(403)
    comments.delete_comment_from_recipe(comment_id)
    return redirect(request.referrer)

@app.route("/like_recipe/<string:recipe_id>", methods=["POST"])
def like_recipe(recipe_id):
    if request.form["csrf_token"] == session["csrf_token"]:
        likes.like_recipe(recipe_id)
        return redirect(request.referrer)
    else:
        abort(403)

@app.route("/hate_recipe/<string:recipe_id>", methods=["POST"])
def hate_recipe(recipe_id):
    if request.form["csrf_token"] == session["csrf_token"]:
        likes.hate_recipe(recipe_id)
        return redirect(request.referrer)
    else:
        abort(403)

@app.route("/delete_recipe", methods=["POST"])
def delete_recipe():
    if request.form["csrf_token"] != session["csrf_token"]:
        abort(403)
    recipe_id = request.form["recipe_id"]
    user_id = users.get_user_id_from_name(session["username"])
    success = recipes.delete_recipe(recipe_id, user_id)

    if success:
        message="Recipe deleted successfully"
    else:
        message="Recipe could not be deleted"
    return render_template("index.html", message=message)

@app.route("/change_password", methods=["POST", "GET"])
def change_password():
    if request.method == "GET":
        return render_template("change_password.html")
    if request.form["csrf_token"] != session["csrf_token"]:
        abort(403)
    user_id = users.get_user_id_from_name(session["username"])
    print("USERID POST", user_id)
    password_old = request.form["password_old"]
    print("password old", password_old)
    p1 = request.form["newpassword"]
    p2 = request.form["newpassword2"]
    result = users.change_password(user_id, password_old, p1, p2)
    if result == True:
        return render_template("profile.html", profile_name=session["username"], message="Password changed!")
    else:
        return render_template("change_password.html", error=result)

@app.route("/add_ingredient_search", methods=["POST"])
def add_ingredient_search():
    recipe_name = request.form["recipe_name"]
    username = request.form["username"]
    active_time = request.form["active_time"]
    passive_time = request.form["passive_time"]
    order_name = request.form["order_name"]
    difficulty = request.form['difficulty']
    meal_type = request.form['meal_type']
    ingredient_list = request.form.getlist('ingredient')
    ingredient_list.append("")
    result = recipes.recipe_search_POST(recipe_name, username, active_time, passive_time, order_name, difficulty, meal_type, ingredient_list)
    return render_template("recipe_list.html", direction="/recipe/", list=result, meal_types=meal_categories.meal_types, ingredient_list=ingredient_list, order_selected=order_name)

@app.route("/remove_ingredient_search", methods=["POST"])
def remove_ingredient_search():
    recipe_name = request.form["recipe_name"]
    username = request.form["username"]
    active_time = request.form["active_time"]
    passive_time = request.form["passive_time"]
    order_name = request.form["order_name"]
    difficulty = request.form['difficulty']
    meal_type = request.form['meal_type']
    ingredient_list = request.form.getlist('ingredient')
    if len(ingredient_list) > 0:
        ingredient_list.pop()
    result = recipes.recipe_search_POST(recipe_name, username, active_time, passive_time, order_name, difficulty, meal_type, ingredient_list)
    return render_template("recipe_list.html", direction="/recipe/", list=result, meal_types=meal_categories.meal_types, ingredient_list=ingredient_list, order_selected=order_name)



#@app.route("/testi", methods=["GET"])
#def testi():
#    return render_template("test_site.html", profile_name=session["username"])