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
