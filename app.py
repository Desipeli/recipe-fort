from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import secrets
from os import getenv

app = Flask(__name__)
#sk = secrets.token_hex(16)
sk = "1234"
app.secret_key = sk
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://xcmtfjejnbuxtr:339bac816f420d0bdffa1acbd75e3d7532303b790df96c3bb41d107a112feb74@ec2-34-246-227-219.eu-west-1.compute.amazonaws.com:5432/d1eggqra1p7gfb"
#"postgresql:///desideri"
db = SQLAlchemy(app)

import routes
