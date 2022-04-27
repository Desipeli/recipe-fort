from db import db
from flask import session
from datetime import datetime
import math
import meal_categories

def recipe(recipe_id):
    sql = "SELECT I.name, I.amount, R.name, R.meal_type, R.difficulty, R. active_time, R.passive_time, R.timestamp FROM  Ingredients I, Recipes R WHERE R.id=:recipe_id AND I.recipe_id=:recipe_id"
    result = db.session.execute(sql, {"recipe_id":recipe_id}).fetchall()
    sql = "SELECT I.text FROM Instructions I WHERE recipe_id=:recipe_id"
    instructions = db.session.execute(sql, {"recipe_id":recipe_id}).fetchone()
    sql = "SELECT U.username FROM Users U, Recipes R WHERE R.user_id=U.id AND R.id=:recipe_id"
    username = db.session.execute(sql, {"recipe_id":recipe_id}).fetchone()
    if instructions == None:
        instructions = ["Missing instructions"]
    return (result[0][2], result, instructions[0], result[0][3], result[0][4], result[0][5], result[0][6], result[0][7], username.username)

def recipe_search_GET():
    sql = "SELECT R.id, R.name, U.username FROM Recipes R, Users U WHERE R.user_id=U.id"
    return db.session.execute(sql).fetchall()

def recipe_search_user(uname):
    sql = "SELECT R.id, R.name, U.username FROM Recipes R, Users U WHERE R.user_id=U.id AND U.username=:uname"
    result = db.session.execute(sql, {"uname":uname})
    return result

def recipe_search_POST(recipe_name, username, active_time, passive_time, order_name, difficulty, meal_type):
    if difficulty == "": difficulty = 3
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
    return result

def check_recipe(recipe_name, active_time, passive_time, ingredients, amounts, units, instructions, difficulty, meal_type):
    meal_types = meal_categories.meal_types
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
    sql = "SELECT R.name FROM Recipes R, Users U WHERE R.name=:recipe_name AND R.user_id=U.id AND U.username=:uname"
    result = db.session.execute(sql, {"recipe_name":recipe_name, "uname":session["username"]}).fetchone()
    if result:
        error = True
        recipe_name_error = "You have already created recipe with this name"
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
    if len(ingredients) < 1:
        error = True
        ingredient_error = "Your recipe must have at least one ingredient"
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
        return recipe_name_error, active_time_error, passive_time_error, ingredient_error, amount_error, unit_error, instructions_error, difficulty_error, meal_type_error
    return None


def create_recipe(recipe_name, active_time, passive_time, ingredients, amounts, units, instructions, difficulty, meal_type):
    try:
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
        return True
    except:
        return False

def add_ingredient(ingredients, amounts, units):
    if ingredients == None:
        ingredients = []
        units = []
        amounts = []
    ingredients.append(" ")
    amounts.append(0)
    units.append(" ")
    return ingredients, amounts, units

def remove_ingredient(ingredients, amounts, units):
    if len(ingredients) > 1:
        ingredients.pop()
        amounts.pop()
        units.pop()
    else:
        ingredients[0] = ""
        amounts[0] = 0
        units[0] = ""
    return ingredients, amounts, units
    