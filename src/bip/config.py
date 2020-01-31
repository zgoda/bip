import os

DEBUG = False
TESTING = False
SECRET_KEY = os.getenv('SECRET_KEY') or 'not so secret'
CSRF_ENABLED = True
LIST_SIZE = 20
