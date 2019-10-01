import pytest
from .. import BIPTests
from flask import url_for


@pytest.mark.usefixtures('client_class')
class TestMiscViews(BIPTests):

    def test_home(self):
        rv = self.client.get(url_for('main.home'))
        assert f'<h1>{self.client.application.site.name}</h1>' in rv.text

    def test_basic_info(self):
        rv = self.client.get(url_for('main.basic_information'))
        assert f'{self.client.application.site.name}</dd>' in rv.text

    def test_staff(self):
        rv = self.client.get(url_for('main.staff'))
        person = self.client.application.site.departments[0].staff[0]
        assert person.person_name in rv.text

    def test_contact(self):
        rv = self.client.get(url_for('main.contact'))
        contact = self.client.application.site.contacts[0]
        assert contact.email in rv.text
