from db import db
from flask import session
from werkzeug.security import check_password_hash, generate_password_hash
import secrets
from datetime import datetime
import string

def get_user_id_from_name(username):
    sql = "SELECT id FROM Users WHERE username=:uname"
    return db.session.execute(sql, {"uname":username}).fetchone()[0]

def login(username, password):
    sql = "SELECT password FROM Users WHERE username=:uname"
    result = db.session.execute(sql, {"uname":username})
    fetched_pw = result.fetchone()
    if fetched_pw:
        if check_password_hash(fetched_pw.password, password):
            session["username"] = username
            session["csrf_token"] = secrets.token_hex(16)
            return True
    return False

def logout():
    del session["username"]

def check_if_user_exists(username):
    sql = "SELECT username FROM Users WHERE username=:uname"
    result = db.session.execute(sql, {"uname":username}).fetchone()
    if result:
        return True
    return False

def check_username_valid(username):
    creation_error = ""
    if len(username) > 20:
        creation_error = "Username must not be over 20 charaters long"
    if len(username) < 3:
        creation_error = "Username must be at least 3 charaters long"
    for letter in username:
        if letter not in string.ascii_letters + string.digits + "åäöÅÄÖ":
            creation_error = "Use only uppercase and lowercase letters and numbers in username"
    return creation_error

def check_password_valid(p1, p2):
    creation_error = ""
    if len(p1) > 20:
        creation_error = "Password must not be over 20 charaters long"
    elif len(p1) < 3:
        creation_error = "Password must be at least 3 characters long"
    elif p1 != p2:
        creation_error = "Passwords did not match"
    #for letter in p1:
    #    if letter not in string.ascii_letters and letter not in string.digits:
    #        creation_error = "Use only uppercase and lowercase letters and numbers in password"
    return creation_error


def register_user(username, password):
    password_hash = generate_password_hash(password)
    ts = datetime.now()
    try:
        sql = "INSERT INTO Users (username, password, admin, timestamp) VALUES (:uname, :pwrd, FALSE, :timestamp)"
        db.session.execute(sql, {"uname":username, "pwrd":password_hash, "timestamp":ts})
        db.session.commit()
    except:
        return False
    return True

def change_password(user_id, password_old, p1, p2):
    sql = "SELECT password FROM Users WHERE id=:user_id"
    stored_old_hash = db.session.execute(sql, {"user_id":user_id}).fetchone()
    db.session.commit()
    error = ""
    if not check_password_hash(stored_old_hash.password, password_old):
        error = "Old password is wrong"
    valid = check_password_valid(p1, p2)
    if valid != "":
        error = valid
    if p1 == password_old or p2 == password_old:
        error = "Old and new passwords are identical"
    if error:
        return error
    password_hash = generate_password_hash(p1)
    sql = "UPDATE Users SET password=:p_hash WHERE id=:user_id"
    db.session.execute(sql, {"p_hash":password_hash, "user_id":user_id})
    db.session.commit()
    return True


