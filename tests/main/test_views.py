from urllib.parse import quote

import pytest
from flask import url_for

from bip.models import Change, ChangeRecord

from .. import BIPTests


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

    def test_get(self, page_factory, user_factory):
        user = user_factory(name='user')
        page = page_factory(
            title='tytuł strony 1', text='tekst strony 1', created_by=user
        )
        rv = self.client.get(url_for('main.page', slug=page.slug))
        assert f'<h2>{page.title}</h2>' in rv.text

    def test_get_with_attachments(self, page_factory, user_factory, attachment_factory):
        user = user_factory(name='user')
        page = page_factory(
            title='tytuł strony 1', text='tekst strony 1', created_by=user
        )
        attachment = attachment_factory(page=page, title='Tytuł załącznika 1')
        rv = self.client.get(url_for('main.page', slug=page.slug))
        file_name = quote(attachment.filename)
        assert f'href="/attachment/{file_name}' in rv.text

    def test_get_notfound(self):
        rv = self.client.get(url_for('main.page', slug='does-not-exist'))
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

    @pytest.mark.parametrize('numpages', [2, 4, 5, 14, 33, 78])
    def test_many_pages(
                self, numpages, config, user_factory, label_factory, page_factory,
                page_label_factory,
            ):
        user = user_factory()
        config['LIST_SIZE'] = 4
        label = label_factory(name='etykieta 1')
        pages = page_factory.create_batch(numpages, created_by=user, updated_by=user)
        for page in pages:
            page_label_factory(page=page, label=label)
        rv = self.client.get(url_for('main.label_page_list', slug=label.slug))
        assert rv.status_code == 200
        assert f'tykieta: {label.name} ({numpages} stro' in rv.text


@pytest.mark.usefixtures('client_class')
class TestChangesView(BIPTests):

    @pytest.fixture(autouse=True)
    def set_up(self):
        self.url = url_for('main.changes')

    def test_no_changes(self):
        rv = self.client.get(self.url)
        assert 'żadnych zarejestrowanych zmian' in rv.text

    def test_changes(self, page_factory, user_factory):
        num = 4
        user = user_factory()
        page_factory.create_batch(num, created_by=user, updated_by=user)
        rv = self.client.get(self.url)
        assert rv.text.count(f'przez: {user.name}') == num

    def test_changes_paginated(self, page_factory, user_factory):
        num = 12
        user = user_factory()
        page_factory.create_batch(num, created_by=user, updated_by=user)
        rv = self.client.get(self.url)
        assert rv.text.count(f'przez: {user.name}') == 10
        assert 'aria-label="następna"' in rv.text

    def test_change_types(self, page_factory, user_factory):
        description = 'dummy'
        user = user_factory()
        page = page_factory(created_by=user, updated_by=user)
        ChangeRecord.log_change(
            page=page, change_type=Change.updated, user=user, description=description
        )
        rv = self.client.get(self.url)
        assert rv.text.count(f'przez: {user.name}') == 2
        assert rv.text.count('rodzaj: utworzenie') == 1
        assert rv.text.count('rodzaj: zmiana') == 1


@pytest.mark.usefixtures('client_class')
class TestSearchView(BIPTests):

    def test_get_no_search(self):
        url = url_for('main.search')
        rv = self.client.get(url)
        assert 'yniki</h3>' not in rv.text

    def test_get_no_results(self):
        query = 'wyszukiwanie'
        url = url_for('main.search', q=query)
        rv = self.client.get(url)
        assert 'yniki</h3>' in rv.text
        assert f'zukany tekst: <strong>{query}</strong>' in rv.text

    def test_get_generic(self, page_factory, label_factory, attachment_factory):
        query = 'wyszukiwanie'
        page = page_factory(title=f'xxx {query} yyy', main=False)
        label = label_factory(name=f'aaa {query} bbb')
        attachment = attachment_factory(page=page, title=f'nnn {query} mmm')
        url = url_for('main.search', q=query)
        rv = self.client.get(url)
        assert 'ie znaleziono stron.' not in rv.text
        assert 'ie znaleziono etykiet.' not in rv.text
        assert 'ie znaleziono załączników.' not in rv.text
        assert page.title in rv.text
        assert label.name in rv.text
        assert attachment.title in rv.text

    def test_get_pages(self, page_factory, label_factory, attachment_factory):
        query = 'wyszukiwanie'
        sections = ['pages']
        page = page_factory(title=f'xxx {query} yyy', main=False)
        label = label_factory(name=f'aaa {query} bbb')
        attachment = attachment_factory(page=page, title=f'nnn {query} mmm')
        url = url_for('main.search', q=query, d=sections)
        rv = self.client.get(url)
        assert 'ie znaleziono stron.' not in rv.text
        assert '<h4>Etykiety</h4>' not in rv.text
        assert '<h4>Załączniki</h4>' not in rv.text
        assert page.title in rv.text
        assert label.name not in rv.text
        assert attachment.title not in rv.text

    def test_get_labels(self, page_factory, label_factory, attachment_factory):
        query = 'wyszukiwanie'
        sections = ['labels']
        page = page_factory(title=f'xxx {query} yyy', main=False)
        label = label_factory(name=f'aaa {query} bbb')
        attachment = attachment_factory(page=page, title=f'nnn {query} mmm')
        url = url_for('main.search', q=query, d=sections)
        rv = self.client.get(url)
        assert '<h4>Strony</h4>' not in rv.text
        assert 'ie znaleziono etykiet.' not in rv.text
        assert '<h4>Załączniki</h4>' not in rv.text
        assert page.title not in rv.text
        assert label.name in rv.text
        assert attachment.title not in rv.text

    def test_get_attachments(self, page_factory, label_factory, attachment_factory):
        query = 'wyszukiwanie'
        sections = ['attachments']
        page = page_factory(title=f'xxx {query} yyy', main=False)
        label = label_factory(name=f'aaa {query} bbb')
        attachment = attachment_factory(page=page, title=f'nnn {query} mmm')
        url = url_for('main.search', q=query, d=sections)
        rv = self.client.get(url)
        assert '<h4>Strony</h4>' not in rv.text
        assert '<h4>Etykiety</h4>' not in rv.text
        assert 'ie znaleziono załączników.' not in rv.text
        assert page.title not in rv.text
        assert label.name not in rv.text
        assert attachment.title in rv.text
