from db import db
from datetime import datetime

def post_comment_to_recipe(user_id, recipe_id, comment):
    if len(comment) == 0 or len(comment) > 10000:
        return
    sql = "INSERT INTO Comments (user_id, recipe_id, text, timestamp) VALUES (:user_id, :recipe_id, :comment, :date)"
    db.session.execute(sql, {"user_id":user_id, "recipe_id":recipe_id, "comment":comment, "date":datetime.now()})
    db.session.commit()

def get_comments_for_recipe(recipe_id):
    sql = "SELECT U.username, C.id, C.text, C.timestamp FROM Comments C, Users U WHERE C.recipe_id=:recipe_id AND C.user_id=U.id ORDER BY timestamp DESC"
    return db.session.execute(sql, {"recipe_id":recipe_id}).fetchall()

def delete_comment_from_recipe(comment_id):
    sql = "DELETE FROM Comments WHERE id=:comment_id"
    db.session.execute(sql, {"comment_id":comment_id})
    db.session.commit()
