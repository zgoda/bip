import pytest

from bip.cli.pages.commands import page_list
from bip.utils.text import truncate_string

from . import BIPCLITests


@pytest.mark.usefixtures('app')
class TestPageOps(BIPCLITests):

    def test_list_no_pages(self):
        rv = self.runner.invoke(page_list)
        assert rv.exit_code == 0
        assert 'żadnych stron' in rv.output

    def test_list_all(self, page_factory):
        p1 = page_factory(active=True)
        p2 = page_factory(active=False)
        rv = self.runner.invoke(page_list)
        assert rv.exit_code == 0
        assert truncate_string(p1.title, 80) in rv.output
        assert truncate_string(p2.title, 80) in rv.output

    def test_list_active_only(self, page_factory):
        p1 = page_factory(active=True)
        p2 = page_factory(active=False)
        rv = self.runner.invoke(page_list, ['--active'])
        assert rv.exit_code == 0
        assert truncate_string(p1.title, 80) in rv.output
        assert truncate_string(p2.title, 80) not in rv.output

    def test_list_inactive_only(self, page_factory):
        p1 = page_factory(active=True)
        p2 = page_factory(active=False)
        rv = self.runner.invoke(page_list, ['--inactive'])
        assert rv.exit_code == 0
        assert truncate_string(p1.title, 80) not in rv.output
        assert truncate_string(p2.title, 80) in rv.output
