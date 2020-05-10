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


@pytest.mark.usefixtures('client_class')
class TestPageViews(BIPTests):

    def test_get_ok(self, page_factory, user_factory):
        user = user_factory(name='user')
        page = page_factory(
            title='tytuł strony 1', text='tekst strony 1', created_by=user
        )
        rv = self.client.get(url_for('main.page', page_id=page.pk))
        assert f'<h2>{page.title}</h2>' in rv.text

    def test_get_notfound(self):
        rv = self.client.get(url_for('main.page', page_id=666))
        assert rv.status_code == 404


@pytest.mark.usefixtures('client_class')
class TestLabelPagesView(BIPTests):

    def test_label_not_found(self):
        rv = self.client.get(url_for('main.label_page_list', slug='dummy'))
        assert rv.status_code == 404

    def test_no_pages(self, label_factory):
        label = label_factory(name='test')
        rv = self.client.get(url_for('main.label_page_list', slug=label.slug))
        assert rv.status_code == 200
        assert f'tykieta: {label.name} (0 stron)' in rv.text

    def test_one_page(self, label_factory, page_factory, page_label_factory):
        label = label_factory(name='etykieta 1')
        page = page_factory(title='tytuł 1', text='tekst 1')
        page_label_factory(label=label, page=page)
        rv = self.client.get(url_for('main.label_page_list', slug=label.slug))
        assert rv.status_code == 200
        assert f'tykieta: {label.name} (1 strona)' in rv.text

    def test_many_pages(
                self, config, label_factory, page_factory, page_label_factory
            ):
        config['LIST_SIZE'] = 4
        label = label_factory(name='etykieta 1')
        pages = page_factory.create_batch(14)
        for page in pages:
            page_label_factory(page=page, label=label)
        rv = self.client.get(url_for('main.label_page_list', slug=label.slug))
        assert rv.status_code == 200
        assert f'tykieta: {label.name} (14 stron)' in rv.text
