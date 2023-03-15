from flask_babel import Babel
from flask_bootstrap import Bootstrap4
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

babel = Babel()
login_manager = LoginManager()
csrf = CSRFProtect()
bootstrap = Bootstrap4()
