import pytest
from werkzeug.datastructures import MultiDict

from bip.utils.forms import ConfirmationForm


@pytest.mark.usefixtures('app')
class TestConfirmationForm:

    def test_confirmed(self):
        f = ConfirmationForm(formdata=MultiDict({'is_confirmed': True}))
        assert f.confirm() is True

    @pytest.mark.parametrize('value', [
        False, '', 'skip'
    ], ids=['false', 'empty', 'missing'])
    def test_not_confirmed(self, value):
        if value == 'skip':
            data = MultiDict({})
        else:
            data = MultiDict({'is_confirmed': value})
        f = ConfirmationForm(formdata=data)
        assert f.confirm() is False
