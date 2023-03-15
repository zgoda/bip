import os

from flask import Flask


class Application(Flask):
    """Overriden application class."""

    @property
    def jinja_options(self) -> dict:
        """Overriden options for Jinja templates.

        :return: template options
        :rtype: dict
        """
        options = dict(super().jinja_options)
        options.update({
            'trim_blocks': True,
            'lstrip_blocks': True,
        })
        return options


def is_test_env() -> bool:
    testing_var = os.environ.get('FLASK_TESTING', '0').lower()
    return testing_var in ['1', 'true', 'yes']
