import os

DEBUG = False
TESTING = False
SECRET_KEY = 'not so secret'
SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or 'sqlite://'
SQLALCHEMY_TRACK_MODIFICATIONS = False
CSRF_ENABLED = True
REDIS_URL = 'redis://localhost:6379/0'
ALLOWED_EXTENSIONS = {'md', 'txt'}
UPLOAD_DIRECTORY = None  # this is set in app initialization code
MAX_CONTENT_LENGTH = 8 * 1024 * 1024  # max upload size: 8 MB
