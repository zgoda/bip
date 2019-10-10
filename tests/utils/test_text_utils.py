import pytest

from bip.utils.text import VALUE_NO, VALUE_YES, text_changes, yesno


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

    def test_changes_not_different(self):
        t1 = '\n'.join([
            'A',
            'B',
        ])
        t2 = '\n'.join([
            'A',
            'B',
        ])
        assert len(text_changes(t1, t2)) == 0

    def test_changes_line_added(self):
        extra = 'C'
        t1 = '\n'.join([
            'A',
            'B',
        ]) + '\n'
        t2 = '\n'.join([
            'A',
            'B',
            extra
        ]) + '\n'
        rv = text_changes(t1, t2)
        assert rv[0].strip().startswith('+')
        assert rv[0].strip().endswith(extra)

    def test_changes_line_removed(self):
        extra = 'B'
        t1 = '\n'.join([
            'A',
            extra,
        ]) + '\n'
        t2 = '\n'.join([
            'A',
        ]) + '\n'
        rv = text_changes(t1, t2)
        assert rv[0].strip().startswith('-')
        assert rv[0].strip().endswith(extra)

    def test_changes_line_changed(self):
        c1 = 'B'
        c2 = 'C'
        t1 = '\n'.join([
            'A',
            c1,
        ]) + '\n'
        t2 = '\n'.join([
            'A',
            c2,
        ]) + '\n'
        rv = text_changes(t1, t2)
        assert len(rv) == 2
        assert rv[0][0] != rv[1][0]
