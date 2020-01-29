from flask import url_for

from ..utils.menu import MenuItem


def editor_tools():
    return [
        MenuItem('profil', url_for('user.profile')),
        MenuItem('hasło', url_for('user.password_change')),
        MenuItem('wyloguj', url_for('auth.logout')),
    ]


def admin_tools():
    return [
        MenuItem('administracja', url_for('admin.home')),
    ]
