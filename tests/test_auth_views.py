import pytest
from flask import url_for

from . import BIPTests


@pytest.mark.usefixtures('client_class')
class TestAuthViews(BIPTests):

    def test_login_user_exists(self, user_factory):
        url = url_for('main.home')
        rv = self.client.get(url)
        assert 'zaloguj' in rv.text
        password = 'pass_1'
        user = user_factory(name='Ivory Tower', password=password)
        rv = self.login(user.name, password)
        assert 'wyloguj' in rv.text
