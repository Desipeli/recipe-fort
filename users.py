from db import db
from flask import session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import string

def login(username, password):
    sql = "SELECT password FROM Users WHERE username=:uname"
    result = db.session.execute(sql, {"uname":username})
    fetched_pw = result.fetchone()
    if fetched_pw:
        if check_password_hash(fetched_pw.password, password):
            session["username"] = username
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
        if letter not in string.ascii_letters and letter not in string.digits:
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