import pytest
from flask import url_for

from .. import BIPTests


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
