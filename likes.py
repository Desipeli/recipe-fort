from flask import session
from db import db
from datetime import datetime
import users

def check_current_status(recipe_id):
    if session.get("username"):
        user_id = users.get_user_id_from_name(session["username"])
        sql = "SELECT L.liked FROM Likes L WHERE L.user_id=:user_id AND L.recipe_id=:recipe_id"
        result = db.session.execute(sql, {"user_id":user_id, "recipe_id":recipe_id}).fetchone()
        if not result:
            return "Did you like or hate this recipe?"
        elif result.liked == False:
            return "You didn't like this recipe"
        else:
            return "You liked this recipe!"
    return "Log in to like/hate this recipe"
    

def like_recipe(recipe_id):
    if session.get("username"):
        user_id = users.get_user_id_from_name(session["username"])
        if check_current_status(recipe_id) == "Did you like or hate this recipe?":
            sql = "INSERT INTO Likes (recipe_id, user_id, liked, timestamp) VALUES (:recipe_id, :user_id, TRUE, :timestamp)"
        else:
            sql = "UPDATE Likes SET liked=TRUE, timestamp=:timestamp WHERE recipe_id=:recipe_id AND user_id=:user_id"
        db.session.execute(sql, {"recipe_id":recipe_id, "user_id":user_id, "timestamp":datetime.now()})
        db.session.commit()
    return

def hate_recipe(recipe_id):
    if session.get("username"):
        user_id = users.get_user_id_from_name(session["username"])
        if check_current_status(recipe_id) == "Did you like or hate this recipe?":
            sql = "INSERT INTO Likes (recipe_id, user_id, liked, timestamp) VALUES (:recipe_id, :user_id, FALSE, :timestamp)"
        else:
            sql = "UPDATE Likes SET liked=FALSE, timestamp=:timestamp WHERE recipe_id=:recipe_id AND user_id=:user_id"
        db.session.execute(sql, {"recipe_id":recipe_id, "user_id":user_id, "timestamp":datetime.now()})
        db.session.commit()
    return

def likes_and_hates(recipe_id):
    sql_likes = "SELECT count(L.liked) FROM Likes L WHERE L.recipe_id=:recipe_id AND L.liked=TRUE" 
    sql_all = "SELECT count(L.liked) FROM Likes L WHERE L.recipe_id=:recipe_id"
    likes = db.session.execute(sql_likes, {"recipe_id":recipe_id}).fetchone()
    all = db.session.execute(sql_all, {"recipe_id":recipe_id}).fetchone()
    return str(likes[0]) + " / " + str(all[0]) + " users liked this recipe"