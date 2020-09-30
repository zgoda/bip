import json

import pytest

from bip.utils import site


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
        {'role_name': 'X', 'role_type': 'staff'},
        {'role_type': 'staff', 'person_name': 'A'},
        {'role_name': 'X', 'person_name': 'A'}
    ], ids=['name', 'role-name', 'role-type'])
    def test_name_and_role_required(self, data):
        with pytest.raises(TypeError):
            site.StaffMember(**data)

    def test_invalid_role_type(self):
        data = {'role_name': 'X', 'role_type': 'invalid', 'person_name': 'A'}
        with pytest.raises(ValueError, match='role type'):
            site.StaffMember(**data)

    def test_basic_information(self):
        data = {'role_name': 'X', 'role_type': 'staff', 'person_name': 'A'}
        sm = site.StaffMember(**data)
        assert len(sm.basic_information) == 4


class TestDepartment:

    def test_members_required(self):
        data = {'name': 'A'}
        with pytest.raises(TypeError):
            site.Department(**data)

    def test_from_dict(self, faker):
        num_staff = 4
        data = {
            'name': faker.company(),
            'phone': faker.phone_number(),
            'email': faker.company_email(),
            'staff': [
                {
                    'role_name': faker.job(),
                    'role_type': 'staff',
                    'person_name': faker.name(),
                }
            ] * num_staff,
        }
        department = site.Department.from_dict(data)
        assert len(department.staff) == num_staff


class TestSite:

    def make_data(self, name, num_staff, fake):
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

    def test_from_dict(self, faker):
        name = faker.company()
        num_staff = 4
        data = self.make_data(name, num_staff, faker)
        obj = site.Site.from_dict(data)
        assert obj.name == name
        assert len(obj.departments[0].staff) == num_staff
        assert obj.departments[0].name == name

    def test_from_json(self, faker):
        name = faker.company()
        num_staff = 4
        s = json.dumps(self.make_data(name, num_staff, faker), ensure_ascii=False)
        obj = site.Site.from_json(s)
        assert obj.name == name
        assert len(obj.departments[0].staff) == num_staff
        assert obj.departments[0].name == name

    def test_basic_information_no_krs(self, faker):
        name = faker.company()
        num_staff = 4
        data = self.make_data(name, num_staff, faker)
        obj = site.Site.from_dict(data)
        info = dict(obj.basic_information)
        assert 'KRS' not in info

    def test_basic_information_with_krs(self, faker):
        name = faker.company()
        num_staff = 4
        data = self.make_data(name, num_staff, faker)
        data['krs'] = 'qaz123'
        obj = site.Site.from_dict(data)
        info = dict(obj.basic_information)
        assert 'KRS' in info
