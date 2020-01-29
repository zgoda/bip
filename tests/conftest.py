import os

import pytest
from flask.wrappers import Response
from pytest_factoryboy import register
from werkzeug.utils import cached_property

from bip import make_app
from bip.ext import db

from .factories import PageFactory, UserFactory

register(PageFactory)
register(UserFactory)


class TestResponse(Response):

    @cached_property
    def text(self):
        if self.mimetype.startswith('text'):
            return self.data.decode(self.charset)
        return self.data


@pytest.fixture
def app():
    """Pytest fixture that builds app object for testing purposes. This may be
    used separately as lighter weight alternative to `client` or
    `client_class` fixtures provided by :mod:`pytest-flask` in situations
    where test client does not have to be configured. Otherwise it is used by
    :mod:`pytest-flask` to create application object.
    """

    os.environ['FLASK_ENV'] = 'test'
    app = make_app(env='test')
    app.response_class = TestResponse
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
