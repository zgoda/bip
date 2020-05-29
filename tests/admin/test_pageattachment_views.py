import pytest
from flask import url_for

from .. import BIPTests


@pytest.mark.usefixtures('client_class')
class TestPageAttachmentAdminViews(BIPTests):

    @pytest.fixture(autouse=True)
    def set_up(self, page_factory, user_factory, label_factory):
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

    def test_post_fail_unknown_op(self):
        self.login(self.admin.name)
        data = {
            'op': 'dummy',
        }
        rv = self.client.post(self.url, data=data, follow_redirects=True)
        assert rv.status_code == 400
