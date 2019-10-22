from flask import Flask


class Application(Flask):

    @property
    def jinja_options(self) -> dict:
        options = dict(super().jinja_options)
        options.update({
            'trim_blocks': True,
            'lstrip_blocks': True,
        })
        return options
