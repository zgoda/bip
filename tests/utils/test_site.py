from bip.utils import site

import pytest


class TestAddress:

    @pytest.mark.parametrize('data', [
        {'zip_code': '10-100', 'town': 'X'},
        {'street': 'A', 'town': 'X'},
        {'street': 'A', 'zip_code': '10-100'},
    ], ids=['street', 'zip', 'town'])
    def test_all_fields_required(self, data):
        with pytest.raises(TypeError):
            site.Address(**data)

    def test_display_value(self):
        data = {'street': 'A', 'zip_code': '10-100', 'town': 'X'}
        addr = site.Address(**data)
        assert addr.display_value == f'{addr.street}, {addr.zip_code} {addr.town}'
