import pytest

from bip.cli.categories.commands import category_create, category_list
from bip.models import Category

from . import BIPCLITests


@pytest.mark.usefixtures('app')
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

    @pytest.mark.parametrize('active', [True, False], ids=['active', 'inactive'])
    def test_create_directory(self, active, user_factory, mocker):
        user = user_factory(name=self.username, password=self.password, admin=True)
        mocker.patch(
            'bip.cli.categories.commands.login_user', mocker.Mock(return_value=user)
        )
        cat_title = 'test 01'
        args = ['-t', cat_title, '--directory', '-u', user.name]
        if active:
            args.append('--active')
        rv = self.runner.invoke(category_create, args)
        assert rv.exit_code == 0
        assert 'została utworzona' in rv.output
        cat_obj = Category.query.filter_by(title=cat_title).one()
        assert cat_obj.directory is not None
        assert cat_obj.active is active

    @pytest.mark.parametrize('active', [True, False], ids=['active', 'inactive'])
    def test_create_no_directory(self, active, user_factory, mocker):
        user = user_factory(name=self.username, password=self.password, admin=True)
        mocker.patch(
            'bip.cli.categories.commands.login_user', mocker.Mock(return_value=user)
        )
        cat_title = 'test 01'
        args = ['-t', cat_title, '-u', user.name]
        if active:
            args.append('--active')
        rv = self.runner.invoke(category_create, args)
        assert rv.exit_code == 0
        assert 'została utworzona' in rv.output
        cat_obj = Category.query.filter_by(title=cat_title).one()
        assert cat_obj.directory is None
        assert cat_obj.active is active
