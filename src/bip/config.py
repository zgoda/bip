import os

DEBUG = False
TESTING = False
SECRET_KEY = 'not so secret'
SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or 'sqlite://'
SQLALCHEMY_TRACK_MODIFICATIONS = False
CSRF_ENABLED = True
