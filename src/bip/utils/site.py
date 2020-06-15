from __future__ import annotations

import json
from dataclasses import dataclass
from typing import List, Tuple

from werkzeug.utils import cached_property

role_names = {
    'manager': 'kierownik',
    'staff': 'pracownik',
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
    def basic_information(self) -> List[Tuple]:
        return [
            ('nazwa', self.name),
            ('telefon', self.phone),
            ('email', self.email),
        ]


@dataclass
class StaffMember:
    role_name: str
    role_type: str
    person_name: str
    photo_url: str = ''
    phone: str = ''
    email: str = ''

    def __post_init__(self):
        if self.role_type not in role_names:
            raise ValueError('Invalid role type')

    @cached_property
    def basic_information(self) -> List[Tuple]:
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
    phone: str = ''
    email: str = ''
    domain: str = ''
    location: str = ''

    @classmethod
    def from_dict(cls, d: dict) -> Department:
        staff = [StaffMember(**s) for s in d.pop('staff', [])]
        return cls(staff=staff, **d)

    @cached_property
    def basic_information(self) -> List[Tuple]:
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
    address: Address
    contacts: List[Contact]
    departments: List[Department]
    bip_url: str
    nip: str
    regon: str
    short_name: str = ''
    krs: str = ''

    @classmethod
    def from_json(cls, s: str) -> Site:
        return cls.from_dict(json.loads(s))

    @classmethod
    def from_dict(cls, d: dict) -> Site:
        d.pop('$schema', None)
        address = Address(**d.pop('address'))
        contacts = [Contact(**c) for c in d.pop('contacts')]
        departments = [Department.from_dict(data) for data in d.pop('departments')]
        return cls(address=address, contacts=contacts, departments=departments, **d)

    @cached_property
    def basic_information(self) -> List[Tuple]:
        data = [
            ('nazwa', self.name),
            ('NIP', self.nip),
            ('REGON', self.regon),
        ]
        if self.krs:
            data.append(('KRS', self.krs))
        return data


def test_site() -> Site:  # pragma: no cover
    """Generate site data object for tests.

    :return: site data object
    :rtype: Site
    """
    name = 'Test Site'
    site = Site(
        name=name, short_name='Test', nip='1111-22-333-333', regon='1234567',
        bip_url='http://bip.instytucja.info',
        address=Address(street='Street 1', zip_code='05-200', town='Test Town'),
        contacts=[
            Contact(phone='+48 500 666 777 888', email='contact@bip.instytucja.info')
        ],
        departments=[
            Department(
                name='Ogólny',
                staff=[
                    StaffMember(
                        role_name='dyrektor', role_type='manager',
                        person_name='Leokadia Iksińska',
                    )
                ]
            )
        ],
    )
    return site
