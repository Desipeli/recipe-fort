from db import db
from flask import session
from datetime import datetime
import math
import meal_categories

def recipe(recipe_id):
    sql = "SELECT R.name, R.meal_type, R.difficulty, R. active_time, R.passive_time, R.timestamp FROM Recipes R WHERE R.id=:recipe_id"
    result = db.session.execute(sql, {"recipe_id":recipe_id}).fetchone()
    sql = "SELECT name, amount, unit FROM Ingredients WHERE recipe_id=:recipe_id"
    ingredients = db.session.execute(sql, {"recipe_id":recipe_id}).fetchall()
    sql = "SELECT I.text FROM Instructions I WHERE recipe_id=:recipe_id"
    instructions = db.session.execute(sql, {"recipe_id":recipe_id}).fetchone()
    sql = "SELECT U.username FROM Users U, Recipes R WHERE R.user_id=U.id AND R.id=:recipe_id"
    username = db.session.execute(sql, {"recipe_id":recipe_id}).fetchone()
    if instructions == None:
        instructions = ["Missing instructions"]
    return (result, get_ingredients(ingredients), get_amounts(ingredients), get_units(ingredients), instructions[0], username.username)

def get_ingredients(i_list):
    ings = []
    for i in i_list:
        ings.append(i[0])
    return ings

def get_amounts(a_list):
    amnts = []
    for a in a_list:
        amnts.append(a[1])
    return amnts

def get_units(u_list):
    units = []
    for u in u_list:
        units.append(u[2])
    return units

def recipe_search_GET():
    sql = "SELECT R.id, R.name, U.username FROM Recipes R, Users U WHERE R.user_id=U.id ORDER BY R.timestamp DESC"
    return db.session.execute(sql).fetchall()

def recipe_search_user(uname):
    sql = "SELECT R.id, R.name, U.username FROM Recipes R, Users U WHERE R.user_id=U.id AND U.username=:uname ORDER BY R.timestamp DESC"
    result = db.session.execute(sql, {"uname":uname})
    return result

def recipe_search_POST(recipe_name, username, active_time, passive_time, order_name, difficulty, meal_type, ingredient_list = None):
    if difficulty == "": difficulty = 3
    meal_type_column = "meal_type"
    error = None
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
    #sql = "SELECT R.id, R.name, U.username FROM Recipes R, Users U, Ingredients I WHERE R.name LIKE :r_name AND U.username LIKE :username AND U.id = R.user_id AND R.active_time<=:active_time AND R.passive_time<=:passive_time AND difficulty<=:difficulty"
    replacements = {"r_name":"%"+recipe_name+"%", "active_time":active_time, "passive_time":passive_time, "username":"%"+username+"%", "difficulty":difficulty, "meal_type":meal_type}
    if meal_type in meal_categories.meal_types:
        sql += " AND meal_type=:meal_type"
    #if ingredient_list != None:
    #    for i in range(len(ingredient_list)):
    #        if len(ingredient_list[i]) == 0: 
    #            continue
    #        if ingredient_list[i][0] == " " or ingredient_list[-1] == " " or len(ingredient_list) > 100:
    #            continue
    #        sql += f" AND I.name LIKE :ing_{i}"
    #        replacements[f"ing_{i}"] = "%"+ingredient_list[i]+"%"
    #    sql += " AND I.recipe_id=R.id"
    if order_name == "0":
        sql += " ORDER BY R.name ASC"
    elif order_name == "1":
        sql += " ORDER BY R.name DESC"
    elif order_name == "2":
        sql += " ORDER BY R.timestamp DESC"
    elif order_name == "3":
        sql += " ORDER BY R.timestamp ASC"
    result = db.session.execute(sql, replacements).fetchall()
    if len(ingredient_list) == 0:
        return result
    final_result = []
    for r in result:
        ingredients_found = 0
        sql = "SELECT name FROM Ingredients WHERE recipe_id=:recipe_id"
        ing_result = db.session.execute(sql, {"recipe_id":r[0]}).fetchall()
        found = [False for x in range(len(ing_result))]
        for ingredient in ingredient_list:
            ingredient = ingredient.strip()
            if ingredient == "":
                continue
            for i in range(len(ing_result)):
                if found[i] == True:
                    continue
                fetched = ing_result[i]
                if ingredient == fetched[0]:
                    ingredients_found += 1
                    found[i] = True
                    continue 
        if ingredients_found >= len(ing_result):
            final_result.append(r)
    return final_result

def check_recipe(recipe_name, active_time, passive_time, ingredients, amounts, units, instructions, difficulty, meal_type, editing = False):
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
    recipe_name = recipe_name.strip()
    if len(recipe_name) == 0 or len(recipe_name) > 60:
        error = True
        recipe_name_error = "Recipe name must be 1-60 characters long"
    sql = "SELECT R.name FROM Recipes R, Users U WHERE R.name=:recipe_name AND R.user_id=U.id AND U.username=:uname"
    result = db.session.execute(sql, {"recipe_name":recipe_name, "uname":session["username"]}).fetchone()
    if not editing:
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
    for i in range(len(ingredients)):
        ingredients[i] = ingredients[i].strip()
    for i in ingredients:
        if len(i) == 0 or len(i) > 60:
            error = True
            ingredient_error = "ingredients must be 1-60 characters long"
    for a in amounts:
        try:
            float(a)
        except:
            error = True
            amount_error = "Amount must be a number"
    for u in units:
        if len(u) > 60:
            error = True
            unit_error = "Units must be 0-600 characters long"
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
            i_amount = str(amounts[i])
            i_unit = str(units[i])
            sql_insert_ingredients = "INSERT INTO Ingredients (recipe_id, name, amount, unit) VALUES (:recipe_id, :name, :amount, :unit)"
            db.session.execute(sql_insert_ingredients, {"recipe_id":recipe_id, "name":i_name, "amount":i_amount, "unit":i_unit})
        sql_instructions = "INSERT INTO Instructions (recipe_id, text) VALUES (:recipe_id, :text)"
        db.session.execute(sql_instructions, {"recipe_id":recipe_id, "text":instructions})
        db.session.commit()
        return recipe_id
    except:
        return False

def delete_recipe(recipe_id, user_id):
    sql = "SELECT U.id FROM Users U, Recipes R WHERE R.user_id=U.id AND R.id=:recipe_id"
    sql_user_id = db.session.execute(sql, {"recipe_id":recipe_id}).fetchone()[0]
    if user_id != sql_user_id:
        return False
    sql = "DELETE FROM Recipes WHERE id=:recipe_id"
    db.session.execute(sql, {"recipe_id":recipe_id})
    db.session.commit()
    return True

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
    