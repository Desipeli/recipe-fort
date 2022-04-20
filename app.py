from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import secrets
from os import getenv


app = Flask(__name__)
#sk = "1234"
app.secret_key = getenv("SECRET_KEY")
#app.secret_key = sk

import routes
