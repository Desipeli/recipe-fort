from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import secrets
from os import getenv


app = Flask(__name__)
#sk = secrets.token_hex(16)
sk = "1234"
app.secret_key = sk
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
db = SQLAlchemy(app)

import routes
