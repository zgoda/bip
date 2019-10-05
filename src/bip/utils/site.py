import json
from dataclasses import dataclass
from enum import Enum
from typing import List

from werkzeug.utils import cached_property


class RoleType(Enum):
    manager = 'manager'
    staff = 'staff'


role_names = {
    RoleType.manager: 'kierownik',
    RoleType.staff: 'pracownik',
}


@dataclass
class Address:
    street: str
    zip_code: str
    town: str

    @cached_property
    def display_value(self):
        return f'{self.street}, {self.zip_code} {self.town}'


@dataclass
class Contact:
    phone: str
    email: str
    name: str = ''

    @cached_property
    def basic_information(self):
        return [
            ('nazwa', self.name),
            ('telefon', self.phone),
            ('email', self.email),
        ]


@dataclass
class StaffMember:
    role_name: str
    role_type: RoleType
    person_name: str
    photo_url: str = ''
    phone: str = ''
    email: str = ''

    def __post_init__(self):
        if not isinstance(self.role_type, RoleType):
            raise ValueError('invalid role type')

    @cached_property
    def basic_information(self):
        return (
            ('nazwisko', self.person_name),
            ('stanowisko', self.role_name),
            ('telefon', self.phone),
            ('email', self.email),
        )


@dataclass
class Department:
    name: str
    staff: List[StaffMember]
    domain: str = ''
    location: str = ''
    phone: str = ''
    email: str = ''

    @classmethod
    def from_dict(cls, d):
        staff = [StaffMember(**s) for s in d.pop('staff', [])]
        return cls(staff=staff, **d)

    @cached_property
    def basic_information(self):
        return (
            ('nazwa', self.name),
            ('zakres działalności', self.domain),
            ('lokalizacja', self.location),
            ('telefon', self.phone),
            ('email', self.email),
        )


@dataclass
class Site:
    name: str
    short_name: str
    address: Address
    contacts: List[Contact]
    departments: List[Department]
    bip_url: str = ''
    NIP: str = ''
    REGON: str = ''
    KRS: str = ''

    @classmethod
    def from_json(cls, s):
        return cls.from_dict(json.loads(s, encoding='utf-8'))

    @classmethod
    def from_dict(cls, d):
        address = Address(**d.pop('address'))
        contacts = [Contact(**c) for c in d.pop('contacts')]
        departments = [Department.from_dict(data) for data in d.pop('departments')]
        return cls(address=address, contacts=contacts, departments=departments, **d)

    @cached_property
    def basic_information(self):
        data = [
            ('nazwa', self.name),
            ('NIP', self.NIP),
            ('REGON', self.REGON),
        ]
        if self.KRS:
            data.append(('KRS', self.KRS))
        return data


def test_site():
    name = 'Test Site'
    site = Site(
        name=name, short_name='Test',
        address=Address(street='Street 1', zip_code='05-200', town='Test Town'),
        contacts=[
            Contact(phone='+48 500 666 777 888', email='contact@bip.instytucja.info')
        ],
        departments=[
            Department(
                name=name,
                staff=[
                    StaffMember(
                        role_name='dyrektor', role_type=RoleType.manager,
                        person_name='Leokadia Iksińska',
                    )
                ]
            )
        ],
    )
    return site
