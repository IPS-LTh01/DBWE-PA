# app/config.py


import os
# Pfad auf Dateisystem
basedir = os.path.abspath(os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv(os.path.join(basedir, '.env'))

# Klasse für App-Konfiguration
class Config(object):

    # Laden der Umgebungsvariable SECRET_KEY
    SECRET_KEY = os.environ.get('SECRET_KEY')

    # Laden der Umgebungsvariable DATABASE_URI
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI')
                                                            
    SQLALCHEMY_TRACK_MODIFICATIONS = False

