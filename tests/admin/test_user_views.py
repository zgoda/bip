import pytest
from flask import url_for

from bip.models import User

from .. import BIPTests


@pytest.mark.usefixtures('client_class')
class TestUserAdminViews(BIPTests):

    @pytest.fixture(autouse=True)
    def set_up(self, user_factory):
        self.list_url = url_for('admin.user_list')
        self.admin_name = self.admin_pw = 'admin'
        self.admin = user_factory(
            name=self.admin_name, password=self.admin_pw, admin=True,
        )

    def detail_url(self, user):
        return url_for('admin.user_detail', user_pk=user.pk)

    def test_list_view(self, user_factory):
        user_names = ['user1', 'user2', self.admin_name]
        for name in user_names:
            user_factory(name=name, password=name)
        self.login(self.admin_name, self.admin_pw)
        rv = self.client.get(self.list_url)
        for name in user_names:
            assert f'{name}</a></td>' in rv.text

    def test_detail_get(self, user_factory):
        name = pw = 'user_1'
        user = user_factory(name=name, password=pw)
        url = self.detail_url(user)
        self.login(self.admin_name, self.admin_pw)
        rv = self.client.get(url)
        assert f'value="{user.email}"' in rv.text
        assert f'action="{url}"' in rv.text

    def test_detail_post(self, user_factory):
        name = pw = 'user_1'
        user = user_factory(name=name, password=pw)
        user_pk = user.pk
        new_email = 'user1@bip.somewhere.else'
        url = self.detail_url(user)
        self.login(self.admin_name, self.admin_pw)
        data = {
            'email': new_email,
            'active': user.active,
            'admin': user.admin,
        }
        rv = self.client.post(url, data=data, follow_redirects=True)
        user = User.query.get(user_pk)
        assert user.email == new_email
        assert user.email in rv.text
