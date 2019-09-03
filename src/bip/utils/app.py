from flask import Flask


class BIPApplication(Flask):

    @property
    def jinja_options(self):
        options = dict(super().jinja_options)
        options.update({
            'trim_blocks': True,
            'lstrip_blocks': True,
        })
        return options
