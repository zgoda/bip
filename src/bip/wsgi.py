import os

from bip import make_app

application = make_app(os.environ.get('ENV'))
