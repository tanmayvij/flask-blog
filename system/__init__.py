from flask import Flask
app = Flask(__name__)
from flask_sqlalchemy import SQLAlchemy

app.config['SECRET_KEY'] = '959d21577205efa16538037a'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

from system import routes