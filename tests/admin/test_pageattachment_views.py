import io

import pytest
from flask import url_for

from bip.models import Attachment

from .. import BIPTests


@pytest.mark.usefixtures('client_class')
class TestPageAttachmentAdminViews(BIPTests):

    @pytest.fixture(autouse=True)
    def _set_up(self, page_factory, user_factory):
        self.admin = user_factory(name='admin', admin=True, active=True)
        self.page = page_factory(
            title='Tytuł strony 1', text='Treść strony 1', created_by=self.admin
        )
        self.url = url_for('admin.page_attachments', page_pk=self.page.pk)

    def test_get_empty(self):
        self.login(self.admin.name)
        rv = self.client.get(self.url)
        assert 'ie ma żadnych załączników' in rv.text
        assert 'value="remove"' not in rv.text
        assert 'value="add"' in rv.text

    def test_get_att_present(self, attachment_factory):
        attachment = attachment_factory(page=self.page)
        self.login(self.admin.name)
        rv = self.client.get(self.url)
        assert f'{attachment.title}</a>' in rv.text
        assert 'value="remove"' in rv.text
        assert 'value="add"' in rv.text

    def test_post_ok_add_minimal(self):
        data = {
            'op': 'add',
            'file': (io.BytesIO(b'file content'), 'filename.txt'),
        }
        self.login(self.admin.name)
        rv = self.client.post(self.url, data=data, follow_redirects=True)
        assert 'zostały zaktualizowane' in rv.text
        assert Attachment.select().where(Attachment.page == self.page).count() == 1

    def test_post_ok_add_full(self):
        data = {
            'op': 'add',
            'file': (io.BytesIO(b'file content'), 'filename.txt'),
            'title': 'Tytuł załącznika 1',
            'description': 'Opis załącznika 1'
        }
        self.login(self.admin.name)
        rv = self.client.post(self.url, data=data, follow_redirects=True)
        assert 'zostały zaktualizowane' in rv.text
        attachment = Attachment.get_or_none(Attachment.page == self.page)
        assert attachment is not None
        assert attachment.title == data['title']
        assert attachment.description == data['description']

    def test_post_fail_add_invalid(self):
        data = {
            'op': 'add',
            'title': 'Tytuł załącznika 1',
            'description': 'Opis załącznika 1'
        }
        self.login(self.admin.name)
        rv = self.client.post(self.url, data=data, follow_redirects=True)
        assert 'zostały zaktualizowane' not in rv.text
        assert 'To pole jest wymagane.</div>' in rv.text
        assert Attachment.get_or_none(Attachment.page == self.page) is None

    def test_post_ok_remove(self, mocker, attachment_factory):
        attachments = {
            'a1': attachment_factory(page=self.page, title='Załącznik 1'),
            'a2': attachment_factory(page=self.page, title='Załącznik 2'),
        }
        data = {
            'op': 'remove',
            'attachment': [attachments['a1'].pk],
        }
        fake_remove = mocker.Mock()
        mocker.patch('bip.admin.views.os.remove', fake_remove)
        self.login(self.admin.name)
        rv = self.client.post(self.url, data=data, follow_redirects=True)
        assert 'zostały zaktualizowane' in rv.text
        assert Attachment.select().where(Attachment.page == self.page).count() == 1
        assert (
            Attachment.get_or_none(Attachment.title == attachments['a1'].title)
        ) is None
        fake_remove.assert_called_once()

    def test_post_fail_unknown_op(self):
        self.login(self.admin.name)
        data = {
            'op': 'dummy',
        }
        rv = self.client.post(self.url, data=data, follow_redirects=True)
        assert rv.status_code == 400
