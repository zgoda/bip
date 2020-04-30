import pytest

from bip.utils.text import VALUE_NO, VALUE_YES, pluralize, yesno

WORDLIST = ['pączek', 'pączki', 'pączków']


@pytest.mark.parametrize('value,expected', [
    (True, VALUE_YES),
    (False, VALUE_NO)
], ids=['yes', 'no'])
def test_yesno_capitalize_default(value, expected):
    rv = yesno(value)
    assert rv == expected.capitalize()


@pytest.mark.parametrize('value,expected', [
    (True, VALUE_YES),
    (False, VALUE_NO)
], ids=['yes', 'no'])
def test_yesno_no_capitalize(value, expected):
    rv = yesno(value, capitalize=False)
    assert rv == expected


def test_pluralize_singular_positive():
    rv = pluralize(1, WORDLIST)
    assert rv.endswith(WORDLIST[0])


@pytest.mark.parametrize('num', [
    11, 31, 121, 1001, 2301
])
def test_pluralize_singular_negative(num):
    rv = pluralize(num, WORDLIST)
    assert not rv.endswith(WORDLIST[0])


@pytest.mark.parametrize('num', [
    2, 3, 4, 22, 54, 133, 2384
])
def test_pluralize_plural1_positive(num):
    rv = pluralize(num, WORDLIST)
    assert rv.endswith(WORDLIST[1])


@pytest.mark.parametrize('num', [12, 13, 14])
def test_pluralize_plural1_negative(num):
    rv = pluralize(num, WORDLIST)
    assert not rv.endswith(WORDLIST[1])
