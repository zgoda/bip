import json
from dataclasses import dataclass
from enum import Enum
from typing import List

RoleType = Enum('RoleType', ['manager', 'staff'])


@dataclass
class Address:
    __slots__ = ['street', 'zip_code', 'town']
    street: str
    zip_code: str
    town: str


@dataclass
class Contact:
    phone: str
    email: str
    name: str = ''


@dataclass
class StaffMember:
    role_name: str
    role_type: RoleType
    person_name: str
    photo_url: str = ''
    phone: str = ''
    email: str = ''


@dataclass
class Department:
    name: str
    staff: List[StaffMember]
    location: str = ''
    phone: str = ''
    email: str = ''

    @classmethod
    def from_dict(cls, d):
        staff = [StaffMember(**s) for s in d.pop('staff', [])]
        return cls(staff=staff, **d)


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
        address = Address(**d['address'])
        contacts = [Contact(**c) for c in d['contacts']]
        departments = [Department.from_dict(data) for data in d['departments']]
        site = cls(
            name=d['name'], short_name=d['short_name'], address=address,
            contacts=contacts, departments=departments,
            bip_url=d['bip_url'], NIP=d['NIP'], REGON=d['REGON'], KRS=d.get('KRS'),
        )
        return site
