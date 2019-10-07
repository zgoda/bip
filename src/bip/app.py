import os
from logging.config import dictConfig

from flask import render_template
from werkzeug.utils import ImportStringError

from .admin import admin_bp
from .auth import auth_bp
from .ext import babel, bootstrap, csrf, db, login_manager
from .main import main_bp
from .user import user_bp
from .utils.app import BIPApplication
from .utils.site import Site, test_site
from .utils.templates import extra_context, extra_filters


def make_app(env=None):
    flask_environment = os.environ.get('FLASK_ENV', '')
    if flask_environment == 'production':
        configure_logging()
    app = BIPApplication(__name__.split('.')[0])
    configure_app(app, env)
    configure_extensions(app)
    configure_templating(app)
    with app.app_context():
        configure_hooks(app)
        configure_blueprints(app)
        configure_error_handlers(app)

    @app.shell_context_processor
    def make_shell_context():  # pylint: disable=unused-variable
        return {
            'db': db,
        }

    return app


def configure_app(app, env):
    app.config.from_object('bip.config')
    if env is not None:
        try:
            app.config.from_object(f'bip.config_{env}')
        except ImportStringError:
            app.logger.info(f'no environment config for {env}')
    config_local = os.environ.get('CONFIG_LOCAL')
    if config_local:
        app.logger.info(f'local configuration loaded from {config_local}')
        app.config.from_envvar('CONFIG_LOCAL')
    config_secrets = os.environ.get('CONFIG_SECRETS')
    if config_secrets:
        app.logger.info(f'secrets loaded from {config_secrets}')
        app.config.from_envvar('CONFIG_SECRETS')
    upload_dir = os.path.abspath(os.path.join(app.instance_path, 'incoming'))
    os.makedirs(upload_dir, exist_ok=True)
    app.config['UPLOAD_DIRECTORY'] = upload_dir


def configure_hooks(app):

    @app.before_first_request
    def load_site_object():  # pylint: disable=unused-variable
        if app.testing and not os.environ.get('SITE_JSON'):
            site = test_site()
        else:
            site_object_path = os.path.abspath(os.environ['SITE_JSON'])
            with open(site_object_path) as fp:
                site = Site.from_json(fp.read())
        app.site = app.jinja_env.globals['site'] = site


def configure_blueprints(app):
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(user_bp, url_prefix='/user')


def configure_extensions(app):
    db.init_app(app)
    babel.init_app(app)
    csrf.init_app(app)
    bootstrap.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'warning'
    login_manager.login_message = 'Musisz się zalogować by uzyskać dostęp do tej strony'

    @login_manager.user_loader
    def get_user(userid):  # pylint: disable=unused-variable
        from .models import User
        return User.query.get(userid)


def configure_templating(app):
    app.jinja_env.globals.update(extra_context())
    app.jinja_env.filters.update(extra_filters())


def configure_logging():
    dictConfig({
        'version': 1,
        'formatters': {
            'default': {
                'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
            }
        },
        'handlers': {
            'wsgi': {
                'class': 'logging.StreamHandler',
                'stream': 'ext://flask.logging.wsgi_errors_stream',
                'formatter': 'default',
            }
        },
        'root': {
            'level': 'INFO',
            'handlers': ['wsgi'],
        },
    })


def configure_error_handlers(app):

    @app.errorhandler(403)
    def forbidden_page(error):  # pylint: disable=unused-variable
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def page_not_found(error):  # pylint: disable=unused-variable
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error_page(error):  # pylint: disable=unused-variable
        return render_template('errors/500.html'), 500
