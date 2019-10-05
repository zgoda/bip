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


class TestContact:

    @pytest.mark.parametrize('data', [
        {'email': 'email'},
        {'phone': 'phone'},
    ], ids=['phone', 'email'])
    def test_email_and_phone_required(self, data):
        with pytest.raises(TypeError):
            site.Contact(**data)

    def test_basic_information(self):
        data = {'email': 'X', 'phone': 'Y'}
        contact = site.Contact(**data)
        assert len(contact.basic_information) == 3


class TestStaffMember:

    @pytest.mark.parametrize('data', [
        {'role_name': 'X', 'role_type': site.RoleType.staff},
        {'role_type': site.RoleType.staff, 'person_name': 'A'},
        {'role_name': 'X', 'person_name': 'A'}
    ], ids=['name', 'role-name', 'role-type'])
    def test_name_and_role_required(self, data):
        with pytest.raises(TypeError):
            site.StaffMember(**data)

    def test_invalid_role_type(self):
        data = {'role_name': 'X', 'role_type': 'invalid', 'person_name': 'A'}
        with pytest.raises(Exception):
            site.StaffMember(**data)

    def test_basic_information(self):
        data = {'role_name': 'X', 'role_type': site.RoleType.staff, 'person_name': 'A'}
        sm = site.StaffMember(**data)
        assert len(sm.basic_information) == 4
