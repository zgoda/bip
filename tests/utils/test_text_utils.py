import pytest

from bip.utils.text import yesno, VALUE_NO, VALUE_YES


class TestTextUtils:

    @staticmethod
    @pytest.mark.parametrize('value,expected', [
        (True, VALUE_YES),
        (False, VALUE_NO)
    ], ids=['yes', 'no'])
    def test_yesno_capitalize_default(value, expected):
        rv = yesno(value)
        assert rv == expected.capitalize()

    @staticmethod
    @pytest.mark.parametrize('value,expected', [
        (True, VALUE_YES),
        (False, VALUE_NO)
    ], ids=['yes', 'no'])
    def test_yesno_no_capitalize(value, expected):
        rv = yesno(value, capitalize=False)
        assert rv == expected
