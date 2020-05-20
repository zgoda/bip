import pytest

from bip.cli.pages.commands import label_change, label_create, label_list
from bip.models import Label
from bip.utils.text import truncate_string

from . import BIPCLITests


@pytest.mark.usefixtures('app')
class TestLabelOps(BIPCLITests):

    def test_list_no_labels(self):
        rv = self.runner.invoke(label_list)
        assert rv.exit_code == 0
        assert 'żadnych etykiet' in rv.output

    def test_list_labels_present(self, label_factory):
        l1 = label_factory(name='etykieta1')
        l2 = label_factory(name='etykieta2')
        rv = self.runner.invoke(label_list)
        assert rv.exit_code == 0
        assert truncate_string(l1.name, 80) in rv.output
        assert truncate_string(l2.name, 80) in rv.output

    def test_create_with_description(self):
        name = 'etykieta1'
        description = 'Etykieta 1'
        rv = self.runner.invoke(label_create, ['-n', name, '-d', description])
        assert rv.exit_code == 0
        assert f'etykieta {name} została utworzona' in rv.output
        label = Label.get_or_none(Label.name == name)
        assert label is not None
        assert label.description == description

    def test_create_no_description_accept(self, mocker):
        name = 'etykieta1'
        description = 'Etykieta 1'
        mocker.patch(
            'bip.cli.pages.commands.click.confirm', mocker.Mock(return_value=True)
        )
        mocker.patch(
            'bip.cli.pages.commands.click.edit', mocker.Mock(return_value=description)
        )
        rv = self.runner.invoke(label_create, ['-n', name])
        assert rv.exit_code == 0
        assert f'etykieta {name} została utworzona' in rv.output
        label = Label.get_or_none(Label.name == name)
        assert label is not None
        assert label.description == description

    def test_create_no_description_reject(self, mocker):
        name = 'etykieta1'
        mocker.patch(
            'bip.cli.pages.commands.click.confirm', mocker.Mock(return_value=False)
        )
        rv = self.runner.invoke(label_create, ['-n', name])
        assert rv.exit_code == 0
        assert f'etykieta {name} została utworzona' in rv.output
        assert Label.select().filter(Label.name == name).count() == 1

    def test_change_notfound(self, label_factory):
        label_factory(name='etykieta1')
        rv = self.runner.invoke(label_change, ['-n', 'etykieta2'])
        assert rv.exit_code != 0
        assert 'nie istnieje' in rv.output

    def test_change_all(self, label_factory):
        name = 'etykieta1'
        label_factory(name=name, description='Etykieta 1')
        new_name = 'etykieta2'
        new_description = 'Etykieta 2'
        rv = self.runner.invoke(
            label_change, ['-n', name, '--new-name', new_name, '-d', new_description]
        )
        assert rv.exit_code == 0
        assert 'została zmieniona' in rv.output
        label = Label.get_or_none(Label.name == new_name)
        assert label is not None
        assert label.description == new_description

    def test_change_name_only(self, mocker, label_factory):
        name = 'etykieta1'
        description = 'Jakaś etykieta'
        label_factory(name=name, description=description)
        new_name = 'etykieta2'
        mocker.patch(
            'bip.cli.pages.commands.click.confirm', mocker.Mock(return_value=False)
        )
        rv = self.runner.invoke(label_change, ['-n', name, '--new-name', new_name])
        assert rv.exit_code == 0
        assert 'została zmieniona' in rv.output
        label = Label.get_or_none(Label.name == new_name)
        assert label is not None
        assert label.description == description

    def test_change_description_only_from_arg(self, label_factory):
        name = 'etykieta1'
        description = 'Jakaś etykieta'
        label_factory(name=name, description=description)
        new_description = 'Hullabaloo'
        rv = self.runner.invoke(label_change, ['-n', name, '-d', new_description])
        assert rv.exit_code == 0
        assert 'została zmieniona' in rv.output
        label = Label.get_or_none(Label.name == name)
        assert label is not None
        assert label.description == new_description

    def test_change_description_only_from_editor(self, mocker, label_factory):
        name = 'etykieta1'
        description = 'Jakaś etykieta'
        label_factory(name=name, description=description)
        new_description = 'Hullabaloo'
        mocker.patch(
            'bip.cli.pages.commands.click.confirm', mocker.Mock(return_value=True)
        )
        mocker.patch(
            'bip.cli.pages.commands.click.edit',
            mocker.Mock(return_value=new_description),
        )
        rv = self.runner.invoke(label_change, ['-n', name])
        assert rv.exit_code == 0
        assert 'została zmieniona' in rv.output
        label = Label.get_or_none(Label.name == name)
        assert label is not None
        assert label.description == new_description

    def test_change_description_clear(self, mocker, label_factory):
        name = 'etykieta1'
        description = 'Jakaś etykieta'
        label_factory(name=name, description=description)
        mocker.patch(
            'bip.cli.pages.commands.click.confirm', mocker.Mock(return_value=True)
        )
        mocker.patch(
            'bip.cli.pages.commands.click.edit',
            mocker.Mock(return_value=''),
        )
        rv = self.runner.invoke(label_change, ['-n', name])
        assert rv.exit_code == 0
        assert 'została zmieniona' in rv.output
        label = Label.get_or_none(Label.name == name)
        assert label is not None
        assert label.description is None
