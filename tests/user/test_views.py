from flask import url_for

import pytest

from .. import BIPTests


@pytest.mark.usefixtures('client_class')
class TestUserProfileViews(BIPTests):

    @pytest.fixture(autouse=True)
    def set_up(self):
        self.profile_url = url_for('user.profile')

    def test_get_profile(self, user_factory):
        name = password = 'Ivory Tower'
        user = user_factory(name=name, password=password)
        self.login(name, password)
        rv = self.client.get(self.profile_url)
        assert user.email in rv.text

    def test_change_email_nonempty_ok(self, user_factory):
        name = password = 'Ivory Tower'
        user_factory(name=name, password=password)
        self.login(name, password)
        new_email = 'new.email@bip.some.where.net'
        data = {
            'email': new_email,
        }
        rv = self.client.post(self.profile_url, data=data, follow_redirects=True)
        assert new_email in rv.text

    def test_change_email_nonempty_fail(self, user_factory):
        name = password = 'Ivory Tower'
        user_factory(name=name, password=password)
        self.login(name, password)
        new_email = 'this is not a valid email'
        data = {
            'email': new_email,
        }
        rv = self.client.post(self.profile_url, data=data, follow_redirects=True)
        assert 'is-invalid' in rv.text
        assert 'Nieprawidłowy adres e-mail' in rv.text

    def test_change_email_empty(self, user_factory):
        name = password = 'Ivory Tower'
        user = user_factory(name=name, password=password)
        self.login(name, password)
        new_email = ''
        data = {
            'email': new_email,
        }
        rv = self.client.post(self.profile_url, data=data, follow_redirects=True)
        assert user.email not in rv.text
