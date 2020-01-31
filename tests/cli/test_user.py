import pytest

from bip.cli.users.commands import (
    user_change, user_create, user_info, user_list, user_login,
)
from bip.models import User

from . import BIPCLITests


class TestUserOps(BIPCLITests):

    def test_user_login(self, mocker, user_factory):
        user_factory(name=self.username, password=self.password)
        fake_setpassword = mocker.Mock()
        fake_keyring = mocker.Mock(
            set_password=fake_setpassword,
            get_password=mocker.Mock(return_value=self.password),
        )
        mocker.patch('bip.utils.cli.keyring', fake_keyring)
        rv = self.runner.invoke(user_login, ['-n', self.username])
        assert rv.exit_code == 0
        fake_setpassword.assert_called_once()

    def test_user_login_clear(self, mocker, user_factory):
        user_factory(name=self.username, password=self.password)
        mocker.patch('bip.cli.users.commands.login_user')
        fake_delpassword = mocker.Mock()
        fake_keyring = mocker.Mock(delete_password=fake_delpassword)
        mocker.patch('bip.cli.users.commands.keyring', fake_keyring)
        rv = self.runner.invoke(
            user_login, ['-n', self.username, '-c']
        )
        assert rv.exit_code == 0
        assert 'zostały usunięte' in rv.output
        fake_delpassword.assert_called_once()

    def test_user_list_empty(self):
        rv = self.runner.invoke(user_list)
        assert rv.exit_code == 0
        assert 'żadnych kont' in rv.output

    def test_user_list_all(self, user_factory):
        u1 = user_factory(name='u1', password='p1', active=True)
        u2 = user_factory(name='u2', password='p2', active=False)
        rv = self.runner.invoke(user_list)
        assert rv.exit_code == 0
        assert u1.email in rv.output
        assert u2.email in rv.output

    def test_user_list_active_only(self, user_factory):
        u1 = user_factory(name='u1', password='p1', active=True)
        u2 = user_factory(name='u2', password='p2', active=False)
        rv = self.runner.invoke(user_list, ['--active'])
        assert rv.exit_code == 0
        assert u1.email in rv.output
        assert u2.email not in rv.output

    def test_user_list_inactive_only(self, user_factory):
        u1 = user_factory(name='u1', password='p1', active=True)
        u2 = user_factory(name='u2', password='p2', active=False)
        rv = self.runner.invoke(user_list, ['--inactive'])
        assert rv.exit_code == 0
        assert u1.email not in rv.output
        assert u2.email in rv.output

    def test_user_create(self):
        rv = self.runner.invoke(
            user_create, ['-n', self.username, '-p', self.password, '--active']
        )
        assert rv.exit_code == 0
        assert 'zostało założone' in rv.output

    def test_user_change_noop(self, mocker, user_factory):
        admin = user_factory(name='admin', password='admin', admin=True)
        user_factory(name=self.username, password=self.password)
        fake_login = mocker.Mock(return_value=admin)
        mocker.patch('bip.cli.users.commands.login_user', fake_login)
        rv = self.runner.invoke(
            user_change, ['-n', self.username, '-u', 'admin']
        )
        assert rv.exit_code == 0
        assert 'nic do zrobienia' in rv.output

    def test_user_change_user_not_found(self, mocker, user_factory):
        admin = user_factory(name='admin', password='admin', admin=True)
        fake_login = mocker.Mock(return_value=admin)
        mocker.patch('bip.cli.users.commands.login_user', fake_login)
        new_email = 'new.email@instytucja.pl'
        rv = self.runner.invoke(
            user_change, ['-n', self.username, '-e', new_email, '-u', 'admin']
        )
        assert rv.exit_code != 0
        assert 'nie znaleziono konta' in rv.output

    def test_user_change_email(self, mocker, user_factory):
        admin = user_factory(name='admin', password='admin', admin=True)
        user_factory(name=self.username, password=self.password)
        fake_login = mocker.Mock(return_value=admin)
        mocker.patch('bip.cli.users.commands.login_user', fake_login)
        new_email = 'new.email@instytucja.pl'
        rv = self.runner.invoke(
            user_change, ['-n', self.username, '-e', new_email, '-u', 'admin']
        )
        assert rv.exit_code == 0
        assert 'zostały zmienione' in rv.output
        user_obj = User.get(User.name == self.username)
        assert user_obj.email == new_email

    def test_user_change_email_self(self, mocker, user_factory):
        actor = user_factory(name=self.username, password=self.password)
        fake_login = mocker.Mock(return_value=actor)
        mocker.patch('bip.cli.users.commands.login_user', fake_login)
        new_email = 'new.email@instytucja.pl'
        rv = self.runner.invoke(
            user_change, ['-n', self.username, '-e', new_email, '-u', self.username]
        )
        assert rv.exit_code == 0
        assert 'zostały zmienione' in rv.output
        user_obj = User.get(User.name == self.username)
        assert user_obj.email == new_email

    def test_user_change_active(self, mocker, user_factory):
        admin = user_factory(name='admin', password='admin', admin=True)
        user_factory(name=self.username, password=self.password)
        fake_login = mocker.Mock(return_value=admin)
        mocker.patch('bip.cli.users.commands.login_user', fake_login)
        rv = self.runner.invoke(
            user_change, ['-n', self.username, '--inactive', '-u', 'admin']
        )
        assert rv.exit_code == 0
        assert 'zostały zmienione' in rv.output
        user_obj = User.get(User.name == self.username)
        assert not user_obj.active

    def test_user_change_active_non_admin(self, mocker, user_factory):
        actor = user_factory(name='actor', password='actor')
        user_factory(name=self.username, password=self.password)
        fake_login = mocker.Mock(return_value=actor)
        mocker.patch('bip.cli.users.commands.login_user', fake_login)
        rv = self.runner.invoke(
            user_change, ['-n', self.username, '--inactive', '-u', 'actor']
        )
        assert rv.exit_code == 1
        assert 'tylko administrator' in rv.output

    @pytest.mark.parametrize('logged_in', [
        'pass', None
    ], ids=['logged-in', 'not-logged-in'])
    def test_user_check_login(self, logged_in, mocker):
        fake_keyring = mocker.Mock(get_password=mocker.Mock(return_value=logged_in))
        mocker.patch('bip.cli.users.commands.keyring', fake_keyring)
        rv = self.runner.invoke(user_info, ['-u', self.username])
        assert rv.exit_code == 0
        if logged_in:
            expected = f'{self.username}: zalogowany'
        else:
            expected = f'{self.username}: niezalogowany'
        assert expected in rv.output
