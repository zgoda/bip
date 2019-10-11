import pytest
import click

from bip.utils.cli import login_user


@pytest.mark.usefixtures('app')
class TestCLIUtils:

    def test_user_login_nonadmin_ok(self, mocker, user_factory):
        password = 'user1'
        user = user_factory(name='user1', password=password, admin=False)
        mocker.patch(
            'bip.utils.cli.keyring',
            mocker.MagicMock(get_password=mocker.Mock(return_value=password)),
        )
        assert login_user(user.name, admin=False) == user

    def test_user_login_nonadmin_fail(self, mocker, user_factory):
        password = 'user1'
        user = user_factory(name='user1', password=password, admin=False)
        mocker.patch(
            'bip.utils.cli.keyring',
            mocker.MagicMock(get_password=mocker.Mock(return_value=password)),
        )
        with pytest.raises(click.ClickException):
            login_user(user.name, admin=True)

    def test_user_login_no_account(self, mocker):
        mocker.patch('bip.utils.cli.click.echo')
        mocker.patch('bip.utils.cli.click.prompt', mocker.Mock(return_value='pass'))
        with pytest.raises(click.ClickException):
            login_user('user2', admin=False)
