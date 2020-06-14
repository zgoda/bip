from flask import Flask


class Application(Flask):
    """Overriden application class.
    """

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
