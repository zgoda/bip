from . import BIPCLITests

from bip.cli.categories.commands import category_list


class TestCategoryOps(BIPCLITests):

    def test_list_no_categories(self):
        rv = self.runner.invoke(category_list)
        assert rv.exit_code == 0
        assert 'żadnych kategorii' in rv.output

    def test_list_all(self, category_factory):
        c1 = category_factory(active=True)
        c2 = category_factory(active=False)
        rv = self.runner.invoke(category_list)
        assert rv.exit_code == 0
        assert c1.title in rv.output
        assert c2.title in rv.output

    def test_list_active_only(self, category_factory):
        c1 = category_factory(active=True)
        c2 = category_factory(active=False)
        rv = self.runner.invoke(category_list, ['--active'])
        assert rv.exit_code == 0
        assert c1.title in rv.output
        assert c2.title not in rv.output

    def test_list_inactive_only(self, category_factory):
        c1 = category_factory(active=True)
        c2 = category_factory(active=False)
        rv = self.runner.invoke(category_list, ['--inactive'])
        assert rv.exit_code == 0
        assert c1.title not in rv.output
        assert c2.title in rv.output
