import os

DEBUG = False
TESTING = False
SECRET_KEY = os.getenv('SECRET_KEY') or 'not so secret'
CSRF_ENABLED = True
LIST_SIZE = 20
MAX_CONTENT_LENGTH = 32 * 1024 * 1024  # 32 megabytes
ATTACHMENTS_DIR = os.getenv('ATTACHMENTS_DIR') or 'attachments'
