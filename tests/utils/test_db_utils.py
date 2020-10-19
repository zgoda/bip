import os

import pytest

from bip.models import get_db_driver


@pytest.mark.parametrize('name', ['SQLite', 'postgres', 'MySQL'])
def test_get_db_driver_name(name, mocker):
    mocker.patch.dict('os.environ', {'DB_DRIVER': name})
    assert get_db_driver() == name.lower()


@pytest.mark.parametrize('value', [None, '', ' '], ids=['none', 'empty', 'space'])
def test_get_db_driver_name_fallback(value, mocker):
    if value is not None:
        mocker.patch.dict('os.environ', {'DB_DRIVER': value})
    else:
        to_remove = ['DB_DRIVER']
        environ = {k: v for k, v in os.environ.items() if k not in to_remove}
        mocker.patch.dict('os.environ', environ, clear=True)
    assert get_db_driver() == 'sqlite'
