import os

import pytest
from flask.wrappers import Response
from pytest_factoryboy import register
from werkzeug.utils import cached_property

from bip import make_app
from bip.models import Attachment, ChangeRecord, Label, Page, PageLabel, User, db

from .factories import (
    AttachmentFactory, LabelFactory, PageFactory, PageLabelFactory, UserFactory,
)

register(PageFactory)
register(UserFactory)
register(LabelFactory)
register(PageLabelFactory)
register(AttachmentFactory)


class TestResponse(Response):

    @cached_property
    def text(self):
        if self.mimetype.startswith('text'):
            return self.data.decode(self.charset)
        return self.data


def fake_gen_password_hash(password):
    return password


def fake_check_password_hash(stored, password):
    return stored == password


@pytest.fixture(scope='session', autouse=True)
def faker_session_locale():
    return ['pl_PL']


@pytest.fixture()
def app(mocker, tmp_path):
    """Pytest fixture that builds app object for testing purposes. This may be
    used separately as lighter weight alternative to `client` or
    `client_class` fixtures provided by :mod:`pytest-flask` in situations
    where test client does not have to be configured. Otherwise it is used by
    :mod:`pytest-flask` to create application object.
    """

    mocker.patch('bip.models.generate_password_hash', fake_gen_password_hash)
    mocker.patch('bip.models.check_password_hash', fake_check_password_hash)
    os.environ['FLASK_ENV'] = 'test'
    app = make_app(env='test')
    app.instance_path = tmp_path
    app.response_class = TestResponse
    models = [Attachment, ChangeRecord, Label, Page, PageLabel, User]
    with app.app_context():
        db.create_tables(models)
        yield app
        db.drop_tables(models)
