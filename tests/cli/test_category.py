import pytest

from bip.cli.categories.commands import category_change, category_create, category_list
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

    def test_list_structure(self, category_factory):
        c1 = category_factory(active=True)
        c2 = category_factory(active=True, parent=c1)
        rv = self.runner.invoke(category_list)
        assert rv.exit_code == 0
        assert rv.output.count(c1.title) == 2
        assert c2.title in rv.output

    @pytest.mark.parametrize('active', [True, False], ids=['active', 'inactive'])
    def test_create(self, active, user_factory, mocker):
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
        assert cat_obj.active is active

    def test_change_title(self, category_factory, user_factory, mocker):
        user = user_factory(name=self.username, password=self.password, admin=True)
        mocker.patch(
            'bip.cli.categories.commands.login_user', mocker.Mock(return_value=user)
        )
        orig_title = 'test 01'
        new_title = 'test 01 changed'
        c = category_factory(title=orig_title, active=True)
        rv = self.runner.invoke(
            category_change, ['-c', c.pk, '-t', new_title, '-u', user.name]
        )
        assert rv.exit_code == 0
        assert 'została zmieniona' in rv.output
        cat_obj = Category.query.filter_by(title=new_title).first()
        assert cat_obj is not None

    def test_change_active(self, category_factory, user_factory, mocker):
        user = user_factory(name=self.username, password=self.password, admin=True)
        mocker.patch(
            'bip.cli.categories.commands.login_user', mocker.Mock(return_value=user)
        )
        title = 'test 01'
        c = category_factory(title=title, active=True)
        rv = self.runner.invoke(
            category_change, ['-c', c.pk, '--inactive', '-u', user.name]
        )
        assert rv.exit_code == 0
        assert 'została zmieniona' in rv.output
        assert Category.query.filter_by(title=title).first().active is False

    def test_change_order(self, category_factory, user_factory, mocker):
        user = user_factory(name=self.username, password=self.password, admin=True)
        mocker.patch(
            'bip.cli.categories.commands.login_user', mocker.Mock(return_value=user)
        )
        title = 'test 01'
        order = 10
        new_order = 20
        c = category_factory(title=title, active=True, menu_order=order)
        rv = self.runner.invoke(
            category_change, ['-c', c.pk, '-o', new_order, '-u', user.name]
        )
        assert rv.exit_code == 0
        assert 'została zmieniona' in rv.output
        assert Category.query.filter_by(title=title).first().menu_order == new_order

    def test_change_parent(self, category_factory, user_factory, mocker):
        user = user_factory(name=self.username, password=self.password, admin=True)
        mocker.patch(
            'bip.cli.categories.commands.login_user', mocker.Mock(return_value=user)
        )
        c1 = category_factory()
        c2 = category_factory()
        child_pk = c1.pk
        parent_pk = c2.pk
        assert Category.query.filter_by(pk=child_pk).first().parent_pk is None
        rv = self.runner.invoke(
            category_change, ['-c', child_pk, '-p', parent_pk, '-u', user.name]
        )
        assert rv.exit_code == 0
        assert 'została zmieniona' in rv.output
        assert Category.query.filter_by(pk=child_pk).first().parent_pk == parent_pk

    def test_change_parent_fail_notfound(self, category_factory, user_factory, mocker):
        user = user_factory(name=self.username, password=self.password, admin=True)
        mocker.patch(
            'bip.cli.categories.commands.login_user', mocker.Mock(return_value=user)
        )
        c = category_factory()
        child_pk = c.pk
        parent_pk = 666
        assert Category.query.filter_by(pk=child_pk).first().parent_pk is None
        rv = self.runner.invoke(
            category_change, ['-c', child_pk, '-p', parent_pk, '-u', user.name]
        )
        assert rv.exit_code != 0
        assert f'znaleziono kategorii nadrzędnej o ID {parent_pk}' in rv.output

    def test_change_parent_fail_self(self, category_factory, user_factory, mocker):
        user = user_factory(name=self.username, password=self.password, admin=True)
        mocker.patch(
            'bip.cli.categories.commands.login_user', mocker.Mock(return_value=user)
        )
        c = category_factory()
        child_pk = c.pk
        parent_pk = child_pk
        assert Category.query.filter_by(pk=child_pk).first().parent_pk is None
        rv = self.runner.invoke(
            category_change, ['-c', child_pk, '-p', parent_pk, '-u', user.name]
        )
        assert rv.exit_code != 0
        assert 'nie może być nadrzędna wobec samej siebie' in rv.output

    def test_change_title_no_effect(self, category_factory, user_factory, mocker):
        user = user_factory(name=self.username, password=self.password, admin=True)
        mocker.patch(
            'bip.cli.categories.commands.login_user', mocker.Mock(return_value=user)
        )
        orig_title = 'test 01'
        new_title = '   '
        c = category_factory(title=orig_title, active=True)
        rv = self.runner.invoke(
            category_change, ['-c', c.pk, '-t', new_title, '-u', user.name]
        )
        assert rv.exit_code == 0
        assert 'bez zmian' in rv.output

    def test_change_noop(self, category_factory, user_factory, mocker):
        user = user_factory(name=self.username, password=self.password, admin=True)
        mocker.patch(
            'bip.cli.categories.commands.login_user', mocker.Mock(return_value=user)
        )
        title = 'test 01'
        c = category_factory(title=title, active=True)
        rv = self.runner.invoke(
            category_change, ['-c', c.pk, '-u', user.name]
        )
        assert rv.exit_code == 0
        assert 'bez zmian' in rv.output

    def test_change_fail_not_found(self, category_factory, user_factory, mocker):
        user = user_factory(name=self.username, password=self.password, admin=True)
        mocker.patch(
            'bip.cli.categories.commands.login_user', mocker.Mock(return_value=user)
        )
        title = 'test 01'
        c = category_factory(title=title, active=True)
        rv = self.runner.invoke(
            category_change, ['-c', c.pk + 666, '-u', user.name]
        )
        assert rv.exit_code != 0
        assert 'Nie znaleziono kategorii' in rv.output
