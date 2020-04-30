import json

import pytest
from faker import Faker

from bip.utils import site

fake = Faker('pl_PL')


class TestAddress:

    @staticmethod
    @pytest.mark.parametrize('data', [
        {'zip_code': '10-100', 'town': 'X'},
        {'street': 'A', 'town': 'X'},
        {'street': 'A', 'zip_code': '10-100'},
    ], ids=['street', 'zip', 'town'])
    def test_all_fields_required(data):
        with pytest.raises(TypeError):
            site.Address(**data)

    @staticmethod
    def test_display_value():
        data = {'street': 'A', 'zip_code': '10-100', 'town': 'X'}
        addr = site.Address(**data)
        assert addr.display_value == f'{addr.street}, {addr.zip_code} {addr.town}'


class TestContact:

    @staticmethod
    @pytest.mark.parametrize('data', [
        {'email': 'email'},
        {'phone': 'phone'},
    ], ids=['phone', 'email'])
    def test_email_and_phone_required(data):
        with pytest.raises(TypeError):
            site.Contact(**data)

    @staticmethod
    def test_basic_information():
        data = {'email': 'X', 'phone': 'Y'}
        contact = site.Contact(**data)
        assert len(contact.basic_information) == 3


class TestStaffMember:

    @staticmethod
    @pytest.mark.parametrize('data', [
        {'role_name': 'X', 'role_type': 'staff'},
        {'role_type': 'staff', 'person_name': 'A'},
        {'role_name': 'X', 'person_name': 'A'}
    ], ids=['name', 'role-name', 'role-type'])
    def test_name_and_role_required(data):
        with pytest.raises(TypeError):
            site.StaffMember(**data)

    @staticmethod
    def test_invalid_role_type():
        data = {'role_name': 'X', 'role_type': 'invalid', 'person_name': 'A'}
        with pytest.raises(ValueError):
            site.StaffMember(**data)

    @staticmethod
    def test_basic_information():
        data = {'role_name': 'X', 'role_type': 'staff', 'person_name': 'A'}
        sm = site.StaffMember(**data)
        assert len(sm.basic_information) == 4


class TestDepartment:

    @staticmethod
    def test_members_required():
        data = {'name': 'A'}
        with pytest.raises(TypeError):
            site.Department(**data)

    @staticmethod
    def test_from_dict():
        num_staff = 4
        data = {
            'name': fake.company(),
            'phone': fake.phone_number(),
            'email': fake.company_email(),
            'staff': [
                {
                    'role_name': fake.job(),
                    'role_type': 'staff',
                    'person_name': fake.name(),
                }
            ] * num_staff,
        }
        department = site.Department.from_dict(data)
        assert len(department.staff) == num_staff


class TestSite:

    def make_data(self, name, num_staff):
        return {
            'name': name,
            'short_name': fake.company_prefix(),
            'address': {
                'street': fake.street_address(),
                'zip_code': fake.postcode(),
                'town': fake.city(),
            },
            'contacts': [
                {
                    'phone': fake.phone_number(),
                    'email': fake.company_email(),
                }
            ],
            'departments': [
                {
                    'name': name,
                    'phone': fake.phone_number(),
                    'email': fake.company_email(),
                    'staff': [
                        {
                            'person_name': fake.name(),
                            'role_name': fake.job(),
                            'role_type': 'staff',
                        }
                    ] * num_staff,
                },
            ],
            'bip_url': fake.url(),
            'nip': fake.company_vat(),
            'regon': fake.regon(),
        }

    def test_from_dict(self):
        name = fake.company()
        num_staff = 4
        data = self.make_data(name, num_staff)
        obj = site.Site.from_dict(data)
        assert obj.name == name
        assert len(obj.departments[0].staff) == num_staff
        assert obj.departments[0].name == name

    def test_from_json(self):
        name = fake.company()
        num_staff = 4
        s = json.dumps(self.make_data(name, num_staff), ensure_ascii=False)
        obj = site.Site.from_json(s)
        assert obj.name == name
        assert len(obj.departments[0].staff) == num_staff
        assert obj.departments[0].name == name

    def test_basic_information_no_krs(self):
        name = fake.company()
        num_staff = 4
        data = self.make_data(name, num_staff)
        obj = site.Site.from_dict(data)
        info = dict(obj.basic_information)
        assert 'KRS' not in info

    def test_basic_information_with_krs(self):
        name = fake.company()
        num_staff = 4
        data = self.make_data(name, num_staff)
        data['krs'] = 'qaz123'
        obj = site.Site.from_dict(data)
        info = dict(obj.basic_information)
        assert 'KRS' in info
