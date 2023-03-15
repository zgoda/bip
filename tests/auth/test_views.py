import pytest
from flask import url_for

from .. import BIPTests


@pytest.mark.usefixtures('client_class')
class TestLogin(BIPTests):

    def test_login_user_exists(self, user_factory):
        url = url_for('main.home')
        rv = self.client.get(url)  # type: ignore
        assert 'zaloguj' in rv.text
        password = 'pass_1'
        user = user_factory(name='Ivory Tower', password=password)
        rv = self.login(user.name, password)
        assert 'wyloguj' in rv.text

    def test_login_user_does_not_exist(self):
        password = 'pass_1'
        username = 'Ivory Tower'
        rv = self.login(username, password)
        assert 'nieprawidłowe dane logowania' in rv.text

    def test_login_wrong_password(self, user_factory):
        user = user_factory(name='Ivory Tower', password='pass_1')
        rv = self.login(user.name, 'invalid')
        assert 'nieprawidłowe dane logowania' in rv.text

    def test_logout_user_logged_in(self, user_factory):
        password = 'pass_1'
        user = user_factory(name='Ivory Tower', password=password)
        self.login(user.name, password)
        rv = self.logout()
        assert f'{user.name} wylogowany z systemu' in rv.text

    def test_logout_anonymous(self):
        rv = self.logout(follow_redirects=False)
        assert rv.status_code == 302
        assert url_for('auth.login') in rv.headers['Location']


@pytest.mark.usefixtures('client_class')
class TestLoginView(BIPTests):

    @pytest.fixture(autouse=True)
    def _set_up(self):
        self.url = url_for('auth.login')

    def test_get(self):
        rv = self.client.get(self.url)  # type: ignore
        assert rv.status_code == 200

    def test_post_invalid_login(self):
        data = {
            'username': 'invalid',
            'password': 'invalid',
        }
        rv = self.client.post(  # type: ignore
            self.url, data=data, follow_redirects=True,
        )
        assert 'nieprawidłowe dane logowania' in rv.text

    def test_post_empty_username(self):
        data = {
            'username': '',
            'password': 'invalid',
        }
        rv = self.client.post(  # type: ignore
            self.url, data=data, follow_redirects=True,
        )
        assert 'is-invalid' in rv.text
        assert 'To pole jest wymagane' in rv.text

    def test_post_empty_password(self):
        data = {
            'username': 'invalid',
            'password': '',
        }
        rv = self.client.post(  # type: ignore
            self.url, data=data, follow_redirects=True,
        )
        assert 'is-invalid' in rv.text
        assert 'To pole jest wymagane' in rv.text
