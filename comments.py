from db import db
from datetime import datetime

def post_comment_to_recipe(user_id, recipe_id, comment):
    sql = "INSERT INTO Comments (user_id, recipe_id, text, date) VALUES (:user_id, :recipe_id, :comment, :date)"
    db.session.execute(sql, {"user_id":user_id, "recipe_id":recipe_id, "comment":comment, "date":datetime.now()})
    db.session.commit()

def get_comments_for_recipe(recipe_id):
    sql = "SELECT U.username, C.text, C.date FROM Comments C, Users U WHERE C.recipe_id=:recipe_id AND C.user_id=U.id ORDER BY date DESC"
    return db.session.execute(sql, {"recipe_id":recipe_id}).fetchall()
    