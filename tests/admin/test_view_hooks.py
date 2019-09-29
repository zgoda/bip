import pytest
from flask import url_for

from .. import BIPTests


@pytest.mark.usefixtures('client_class')
class TestAdminViewHooks(BIPTests):

    @pytest.fixture(autouse=True)
    def set_up(self):
        self.admin_url = url_for('admin.home')

    def test_admin_access(self, user_factory):
        admin_pw = 'pw_admin_1'
        admin = user_factory(name='admin', password=admin_pw, admin=True)
        self.login(admin.name, admin_pw)
        rv = self.client.get(self.admin_url)
        assert rv.status_code == 200

    def test_regular_access(self, user_factory):
        regular_pw = 'pw_regular_1'
        regular = user_factory(name='regular', password=regular_pw)
        self.login(regular.name, regular_pw)
        rv = self.client.get(self.admin_url)
        assert rv.status_code == 403

    def test_anon_access(self):
        login_url = url_for('auth.login')
        rv = self.client.get(self.admin_url)
        assert rv.status_code == 302
        assert login_url in rv.headers['Location']
