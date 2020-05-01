from __future__ import annotations

import json
from dataclasses import dataclass
from typing import List, Tuple

from werkzeug.utils import cached_property

role_names = {
    'manager': 'kierownik',
    'staff': 'pracownik',
}


class Serializable:

    SERIALIZE_FIELDS = []

    def to_dict(self):
        return {
            fn: getattr(self, fn) for fn in self.SERIALIZE_FIELDS  # skipcq: PTC-W0034
        }


@dataclass
class Address(Serializable):
    street: str
    zip_code: str
    town: str

    SERIALIZE_FIELDS = ['street', 'zip_code', 'town']

    @cached_property
    def display_value(self):
        return f'{self.street}, {self.zip_code} {self.town}'


@dataclass
class Contact(Serializable):
    phone: str
    email: str
    name: str = ''

    SERIALIZE_FIELDS = ['phone', 'email', 'name']

    @cached_property
    def basic_information(self) -> List[Tuple]:
        return [
            ('nazwa', self.name),
            ('telefon', self.phone),
            ('email', self.email),
        ]


@dataclass
class StaffMember(Serializable):
    role_name: str
    role_type: str
    person_name: str
    photo_url: str = ''
    phone: str = ''
    email: str = ''

    SERIALIZE_FIELDS = [
        'role_name', 'role_type', 'person_name', 'photo_url', 'phone', 'email'
    ]

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
class Department(Serializable):
    staff: List[StaffMember]
    phone: str = ''
    email: str = ''
    name: str = ''
    domain: str = ''
    location: str = ''

    SERIALIZE_FIELDS = ['phone', 'email', 'name', 'domain', 'location']

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

    def to_dict(self):
        rv = super().to_dict()
        rv['staff'] = [p.to_dict() for p in self.staff]
        return rv


@dataclass
class Site(Serializable):
    name: str
    address: Address
    contacts: List[Contact]
    departments: List[Department]
    bip_url: str
    nip: str
    regon: str
    short_name: str = ''
    krs: str = ''

    SERIALIZE_FIELDS = ['name', 'bip_url', 'nip', 'regon', 'short_name', 'krs']

    def __bool__(self):
        if all([
            self.name, self.address, self.contacts, self.departments, self.bip_url,
            self.nip, self.regon,
        ]):
            return True
        return False

    @classmethod
    def new(cls):
        return cls(
            name=None, address=None, contacts=None, departments=None,
            bip_url=None, nip=None, regon=None,
        )

    @classmethod
    def from_json(cls, s: str) -> Site:
        return cls.from_dict(json.loads(s))

    @classmethod
    def from_dict(cls, d: dict) -> Site:
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

    def to_dict(self):
        rv = super().to_dict()
        rv['address'] = self.address.to_dict()
        rv['contacts'] = [c.to_dict() for c in self.contacts]
        rv['departments'] = [d.to_dict() for d in self.departments]
        return rv


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
