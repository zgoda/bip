import pytest


class BIPCLITests:

    @pytest.fixture(autouse=True)
    def _set_up(self, app):
        self.runner = app.test_cli_runner()
        self.username = 'user_1'
        self.password = 'pass'
