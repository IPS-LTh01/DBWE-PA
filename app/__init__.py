# app/init.py
from flask import Flask
# mysql Module laden
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# LoginManager importieren
from flask_login import LoginManager

# app Config laden
from config import Config


app = Flask(__name__)
app.config.from_object(Config)

# SQLAlchemy initialisieren
db = SQLAlchemy(app)
migrate = Migrate(app,db)

# LoginMagaer initialisieren
login = LoginManager(app)
login.login_view = 'login'

import logging
from logging.handlers import RotatingFileHandler
import os

if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('App startup')

from app import routes, models, errors, api