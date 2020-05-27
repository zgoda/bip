import pytest

from bip.cli.attachments.commands import attachment_list
from bip.utils.text import truncate_string

from . import BIPCLITests


@pytest.mark.usefixtures('app')
class TestAttachmentOps(BIPCLITests):

    def test_list_no_attachments(self):
        rv = self.runner.invoke(attachment_list, [])
        assert 'żadnych załączników' in rv.output

    def test_list_ok(self, page_factory, attachment_factory):
        p_title = 'Tytuł strony 1'
        page = page_factory(title=p_title)
        a_title = 'Tytuł załącznika 1'
        attachment_factory(page=page, title=a_title)
        rv = self.runner.invoke(attachment_list, [])
        assert truncate_string(a_title, 80) in rv.output
        assert truncate_string(p_title, 80) in rv.output
