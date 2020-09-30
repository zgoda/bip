import pytest
from flask import url_for
from markdown import markdown

from bip.models import Attachment

from .. import BIPTests


@pytest.mark.usefixtures('client_class')
class TestAttachmentAdminViews(BIPTests):

    @pytest.fixture(autouse=True)
    def _set_up(self, user_factory, page_factory):
        self.list_url = url_for('admin.attachment_list')
        self.admin_name = 'admin'
        self.admin = user_factory(name=self.admin_name, admin=True, active=True)
        self.page = page_factory(created_by=self.admin, updated_by=self.admin)

    @staticmethod
    def detail_url(attachment):
        return url_for('admin.attachment_detail', attachment_pk=attachment.pk)

    def test_list_get(self, attachment_factory):
        titles = ['a1', 'a2']
        for title in titles:
            attachment_factory(page=self.page, title=title)
        self.login(self.admin_name)
        rv = self.client.get(self.list_url)
        for title in titles:
            assert f'>{title}</a>' in rv.text
        page_list_url = url_for('admin.page_list')
        assert f'href="{page_list_url}"' in rv.text

    def test_list_post(self):
        data = {
            'field': 'dummy'
        }
        self.login(self.admin_name)
        rv = self.client.post(self.list_url, data=data)
        assert rv.status_code == 405

    def test_detail_get(self, attachment_factory):
        title = 'Załącznik 1'
        attachment = attachment_factory(page=self.page, title=title)
        url = self.detail_url(attachment)
        self.login(self.admin_name)
        rv = self.client.get(url)
        assert f'value="{title}"' in rv.text
        assert f'action="{url}"' in rv.text

    def test_detail_post(self, attachment_factory):
        title = 'Załącznik 1'
        attachment = attachment_factory(page=self.page, title=title)
        url = self.detail_url(attachment)
        new_title = 'Nowy tytuł'
        new_description = 'Nowy opis'
        data = {
            'title': new_title,
            'description': new_description,
        }
        self.login(self.admin_name)
        rv = self.client.post(url, data=data, follow_redirects=True)
        assert f'>{new_title}</a>' in rv.text
        attachment = Attachment.get_or_none(Attachment.pk == attachment.pk)
        assert attachment is not None
        assert attachment.description_html == markdown(new_description)

    def test_detail_post_clear_description(self, attachment_factory):
        title = 'Załącznik 1'
        description = 'Opis załącznika 1'
        attachment = attachment_factory(
            page=self.page, title=title, description=description
        )
        url = self.detail_url(attachment)
        new_title = 'Nowy tytuł'
        data = {
            'title': new_title,
        }
        self.login(self.admin_name)
        rv = self.client.post(url, data=data, follow_redirects=True)
        assert f'>{new_title}</a>' in rv.text
        attachment = Attachment.get_or_none(Attachment.pk == attachment.pk)
        assert attachment is not None
        assert attachment.description_html is None
