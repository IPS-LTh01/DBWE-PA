# app/config.py

import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'secretkey'
    #SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') #or \
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://DBWE_User:JBa673%4000aj@localhost/DBWE_app' #or \
                                                             #'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

