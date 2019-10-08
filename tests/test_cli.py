import pytest

from bip.cli import user_login, user_list, user_create


class TestCLI:

    @pytest.fixture(autouse=True)
    def set_up(self, app):
        self.runner = app.test_cli_runner()
        self.username = 'user_1'
        self.password = 'pass'

    def test_user_login(self, mocker):
        mocker.patch('bip.cli.login_user')
        fake_setpassword = mocker.Mock()
        fake_keyring = mocker.Mock(set_password=fake_setpassword)
        mocker.patch('bip.cli.keyring', fake_keyring)
        rv = self.runner.invoke(user_login, ['-u', self.username, '-p', self.password])
        assert rv.exit_code == 0
        assert 'zostały zapisane' in rv.output
        fake_setpassword.assert_called_once()

    def test_user_login_clear(self, mocker):
        mocker.patch('bip.cli.login_user')
        fake_delpassword = mocker.Mock()
        fake_keyring = mocker.Mock(delete_password=fake_delpassword)
        mocker.patch('bip.cli.keyring', fake_keyring)
        rv = self.runner.invoke(
            user_login, ['-u', self.username, '-p', self.password, '-c']
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
