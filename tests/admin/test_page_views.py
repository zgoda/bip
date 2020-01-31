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

    def test_list_view(self, page_factory):
        titles = ['page 1', 'page 2']
        for title in titles:
            page_factory(title=title, text=title, created_by=self.admin)
        self.login(self.admin_name)
        rv = self.client.get(self.list_url)
        for title in titles:
            assert f'{title}</a>' in rv.text

    def test_detail_get(self, page_factory):
        title = 'page 1'
        page = page_factory(title=title, text=title, created_by=self.admin)
        url = self.detail_url(page)
        self.login(self.admin_name)
        rv = self.client.get(url)
        assert f'value="{page.title}"' in rv.text
        assert f'action="{url}"' in rv.text
