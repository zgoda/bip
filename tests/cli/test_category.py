from . import BIPCLITests

from bip.cli.categories.commands import category_list


class TestCategoryOps(BIPCLITests):

    def test_list_no_categories(self):
        rv = self.runner.invoke(category_list)
        assert rv.exit_code == 0
        assert 'żadnych kategorii' in rv.output
