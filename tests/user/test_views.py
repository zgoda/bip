import pytest
from flask import url_for

from bip.models import User

from .. import BIPTests


@pytest.mark.usefixtures('client_class')
class TestUserProfileView(BIPTests):

    @pytest.fixture(autouse=True)
    def set_up(self):
        self.url = url_for('user.profile')

    def test_get(self, user_factory):
        name = password = 'Ivory Tower'
        user = user_factory(name=name, password=password)
        self.login(name, password)
        rv = self.client.get(self.url)
        assert user.email in rv.text

    def test_change_email_nonempty_ok(self, user_factory):
        name = password = 'Ivory Tower'
        user_factory(name=name, password=password)
        self.login(name, password)
        new_email = 'new.email@bip.some.where.net'
        data = {
            'email': new_email,
        }
        rv = self.client.post(self.url, data=data, follow_redirects=True)
        assert new_email in rv.text

    def test_change_email_nonempty_fail(self, user_factory):
        name = password = 'Ivory Tower'
        user_factory(name=name, password=password)
        self.login(name, password)
        new_email = 'this is not a valid email'
        data = {
            'email': new_email,
        }
        rv = self.client.post(self.url, data=data, follow_redirects=True)
        assert 'is-invalid' in rv.text
        assert 'Nieprawidłowy adres email' in rv.text

    def test_change_email_empty(self, user_factory):
        name = password = 'Ivory Tower'
        user = user_factory(name=name, password=password)
        self.login(name, password)
        new_email = ''
        data = {
            'email': new_email,
        }
        rv = self.client.post(self.url, data=data, follow_redirects=True)
        assert user.email not in rv.text


@pytest.mark.usefixtures('client_class')
class TestChangePasswordView(BIPTests):

    @pytest.fixture(autouse=True)
    def set_up(self):
        self.url = url_for('user.password_change')
        self.name = self.password = 'Ivory Tower'

    def test_get(self, user_factory):
        user_factory(name=self.name, password=self.password)
        self.login(self.name, self.password)
        rv = self.client.get(self.url)
        assert 'name="new_password"' in rv.text

    def test_change_ok(self, user_factory):
        user = user_factory(name=self.name, password=self.password)
        self.login(self.name, self.password)
        new_password = 'new password'
        data = {
            'new_password': new_password,
            'new_password_repeat': new_password,
        }
        rv = self.client.post(self.url, data=data, follow_redirects=True)
        assert 'zostało pomyślnie zmienione' in rv.text
        user = User.get(User.name == self.name)
        assert user.check_password(new_password)

    def test_change_fail_passwords_differ(self, user_factory):
        user = user_factory(name=self.name, password=self.password)
        self.login(self.name, self.password)
        data = {
            'new_password': 'new password 1',
            'new_password_repeat': 'new password 2',
        }
        rv = self.client.post(self.url, data=data, follow_redirects=True)
        assert 'Hasła muszą być identyczne' in rv.text
        user = User.get(User.name == self.name)
        assert user.check_password(self.password)

    def test_change_fail_password_empty(self, user_factory):
        user = user_factory(name=self.name, password=self.password)
        self.login(self.name, self.password)
        data = {
            'new_password': '',
            'new_password_repeat': '',
        }
        rv = self.client.post(self.url, data=data, follow_redirects=True)
        assert 'To pole jest wymagane' in rv.text
        user = User.get(User.name == self.name)
        assert user.check_password(self.password)
