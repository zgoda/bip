import pytest
from flask import url_for

from .. import BIPTests


@pytest.mark.usefixtures('client_class')
class TestPageAdminViews(BIPTests):

    @pytest.fixture(autouse=True)
    def set_up(self, user_factory):
        self.list_url = url_for('admin.page_list')
        self.admin_name = 'admin'
        self.admin = user_factory(name=self.admin_name, admin=True, active=True)

    @staticmethod
    def detail_url(page):
        return url_for('admin.page_detail', page_pk=page.pk)

    def test_list_get(self, page_factory):
        titles = ['page 1', 'page 2']
        for title in titles:
            page_factory(title=title, text=title, created_by=self.admin)
        self.login(self.admin_name)
        rv = self.client.get(self.list_url)
        for title in titles:
            assert f'>{title}</a>' in rv.text
        assert f'action="{self.list_url}"' in rv.text

    def test_list_post(self):
        title = 'title 1'
        data = {
            'title': title,
            'text': title,
            'active': True,
            'main': True,
        }
        self.login(self.admin_name)
        rv = self.client.post(self.list_url, data=data, follow_redirects=True)
        assert f'>{title}</a>' in rv.text

    def test_detail_get(self, page_factory):
        title = 'page 1'
        page = page_factory(title=title, text=title, created_by=self.admin)
        url = self.detail_url(page)
        self.login(self.admin_name)
        rv = self.client.get(url)
        assert f'value="{page.title}"' in rv.text
        assert f'action="{url}"' in rv.text

    def test_detail_post(self, page_factory):
        title = 'page 1'
        page = page_factory(title=title, text=title, created_by=self.admin)
        url = self.detail_url(page)
        self.login(self.admin_name)
        new_title = 'new title'
        data = {
            'title': new_title,
            'text': page.text,
            'active': page.active,
            'main': page.main
        }
        rv = self.client.post(url, data=data, follow_redirects=True)
        assert f'>{new_title}</a>' in rv.text


@pytest.mark.usefixtures('client_class')
class TestLabelAdminViews(BIPTests):

    @pytest.fixture(autouse=True)
    def set_up(self, user_factory):
        self.list_url = url_for('admin.label_list')
        self.admin_name = 'admin'
        self.admin = user_factory(name=self.admin_name, admin=True, active=True)

    @staticmethod
    def detail_url(label):
        return url_for('admin.label_detail', label_pk=label.pk)

    def test_list_get(self, label_factory):
        names = ['e1', 'e2']
        for name in names:
            label_factory(name=name)
        self.login(self.admin_name)
        rv = self.client.get(self.list_url)
        for name in names:
            assert f'>{name}</a>' in rv.text
        assert f'action="{self.list_url}"' in rv.text

    def test_list_post(self):
        name = 'etykieta 1'
        data = {
            'name': name,
        }
        self.login(self.admin_name)
        rv = self.client.post(self.list_url, data=data, follow_redirects=True)
        assert f'>{name}</a>' in rv.text

    def test_detail_get(self, label_factory):
        name = 'etykieta 1'
        label = label_factory(name=name)
        url = self.detail_url(label)
        self.login(self.admin_name)
        rv = self.client.get(url)
        assert f'value="{label.name}"' in rv.text
        assert f'action="{url}"' in rv.text

    def test_detail_post(self, label_factory):
        name = 'etykieta 1'
        label = label_factory(name=name)
        url = self.detail_url(label)
        new_name = 'odnowiona etykieta 1'
        data = {'name': new_name}
        self.login(self.admin_name)
        rv = self.client.post(url, data=data, follow_redirects=True)
        assert f'>{new_name}</a>' in rv.text


@pytest.mark.usefixtures('client_class')
class TestPageLabelAdminViews(BIPTests):

    @pytest.fixture(autouse=True)
    def set_up(self, page_factory, user_factory, label_factory):
        self.admin = user_factory(name='admin', admin=True, active=True)
        self.page = page_factory(
            title='Tytuł strony 1', text='Treść strony 1', created_by=self.admin
        )
        self.labels = {
            'label1': label_factory(name='etykieta 1'),
            'label2': label_factory(name='etykieta 2'),
        }
        self.url = url_for('admin.page_labels', page_pk=self.page.pk)

    def test_get_empty(self):
        self.login(self.admin.name)
        rv = self.client.get(self.url)
        assert 'ie ma żadnych etykiet' in rv.text
        assert 'value="remove"' not in rv.text
        assert 'value="add"' in rv.text

    def test_get_none_left(self, page_label_factory):
        for label in self.labels.values():
            page_label_factory(page=self.page, label=label)
        self.login(self.admin.name)
        rv = self.client.get(self.url)
        assert 'trona wykorzystuje wszystkie dostępne etykiety' in rv.text
        assert 'value="remove"' in rv.text
        assert 'value="add"' not in rv.text

    def test_post_ok_add(self):
        self.login(self.admin.name)
        data = {
            'op': 'add',
            'label': [str(self.labels['label1'].pk)],
        }
        rv = self.client.post(self.url, data=data, follow_redirects=True)
        assert f'etykiety strony {self.page.title} zostały zmienione' in rv.text
        assert 'value="remove"' in rv.text
        assert 'value="add"' in rv.text

    def test_post_ok_remove(self, page_label_factory):
        page_labels = {}
        for name, label in self.labels.items():
            page_labels[name] = page_label_factory(page=self.page, label=label)
        self.login(self.admin.name)
        data = {
            'op': 'remove',
            'label': [str(page_labels['label1'].pk)],
        }
        rv = self.client.post(self.url, data=data, follow_redirects=True)
        assert f'etykiety strony {self.page.title} zostały zmienione' in rv.text
        assert 'value="remove"' in rv.text
        assert 'value="add"' in rv.text

    def test_post_fail_unknown_op(self):
        self.login(self.admin.name)
        data = {
            'op': 'dummy',
        }
        rv = self.client.post(self.url, data=data, follow_redirects=True)
        assert rv.status_code == 400
