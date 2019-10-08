import pytest

from bip.cli import user_login


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
