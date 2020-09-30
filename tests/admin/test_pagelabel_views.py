import pytest
from flask import url_for

from .. import BIPTests


@pytest.mark.usefixtures('client_class')
class TestPageLabelAdminViews(BIPTests):

    @pytest.fixture(autouse=True)
    def _set_up(self, page_factory, user_factory, label_factory):
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
