import pytest
from flask import url_for

from bip.models import User

from .. import BIPTests


@pytest.mark.usefixtures('client_class')
class TestUserAdminViews(BIPTests):

    @pytest.fixture(autouse=True)
    def _set_up(self, user_factory):
        self.list_url = url_for('admin.user_list')
        self.admin_name = 'admin'
        self.admin = user_factory(
            name=self.admin_name, admin=True, active=True,
        )

    @staticmethod
    def detail_url(user):
        return url_for('admin.user_detail', user_pk=user.pk)

    def test_list_view(self, user_factory):
        user_names = ['user1', 'user2']
        for name in user_names:
            user_factory(name=name)
        self.login(self.admin_name)
        rv = self.client.get(self.list_url)
        for name in user_names:
            assert f'{name}</a></td>' in rv.text

    def test_detail_get(self, user_factory):
        name = 'user_1'
        user = user_factory(name=name)
        url = self.detail_url(user)
        self.login(self.admin_name)
        rv = self.client.get(url)
        assert f'value="{user.email}"' in rv.text
        assert f'action="{url}"' in rv.text

    def test_detail_post_change_ok(self, user_factory):
        name = 'user_1'
        user = user_factory(name=name)
        user_pk = user.pk
        new_email = 'user1@bip.somewhere.else'
        url = self.detail_url(user)
        self.login(self.admin_name)
        data = {
            'email': new_email,
            'active': user.active,
            'admin': user.admin,
        }
        rv = self.client.post(url, data=data, follow_redirects=True)
        user = User.get(user_pk)
        assert f'dane konta {name} zostały zmienione' in rv.text
        assert user.email == new_email

    def test_detail_post_change_fail(self, user_factory):
        name = 'user_1'
        user = user_factory(name=name)
        user_pk = user.pk
        new_email = 'very invalid email'
        url = self.detail_url(user)
        self.login(self.admin_name)
        data = {
            'email': new_email,
            'active': user.active,
            'admin': user.admin,
        }
        rv = self.client.post(url, data=data, follow_redirects=True)
        assert 'is-invalid' in rv.text
        assert 'Nieprawidłowy adres email' in rv.text
        user = User.get(user_pk)
        assert user.email != new_email

    def test_create_ok(self):
        name = 'user_1'
        password = 'pass'
        self.login(self.admin.name)
        data = {
            'name': name,
            'password1': password,
            'password2': password,
        }
        rv = self.client.post(self.list_url, data=data, follow_redirects=True)
        assert 'nowe konto zostało utworzone' in rv.text

    def test_create_fail(self):
        name = 'user_1'
        password = 'pass'
        self.login(self.admin.name)
        data = {
            'name': name,
            'password1': password,
            'password2': 'dummy',
        }
        rv = self.client.post(self.list_url, data=data, follow_redirects=True)
        assert 'is-invalid' in rv.text
        assert 'hasła muszą być identyczne' in rv.text
        assert User.get_or_none(User.name == name) is None
