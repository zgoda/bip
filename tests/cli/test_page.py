import pytest

from bip.cli.pages.commands import (
    label_change, label_create, label_list, page_change, page_create, page_labels,
    page_list,
)
from bip.models import Label, Page, PageLabel
from bip.utils.text import slugify, truncate_string

from . import BIPCLITests


@pytest.mark.usefixtures('app')
class TestPageOps(BIPCLITests):

    @pytest.fixture(autouse=True)
    def set_up2(self, user_factory):
        self.user = user_factory(name=self.username, password=self.password)

    def test_list_no_pages(self):
        rv = self.runner.invoke(page_list)
        assert rv.exit_code == 0
        assert 'żadnych stron' in rv.output

    def test_list_all(self, page_factory):
        p1 = page_factory(active=True, created_by=self.user, updated_by=self.user)
        p2 = page_factory(active=False, created_by=self.user, updated_by=self.user)
        rv = self.runner.invoke(page_list)
        assert rv.exit_code == 0
        assert truncate_string(p1.title, 80) in rv.output
        assert truncate_string(p2.title, 80) in rv.output

    def test_list_active_only(self, page_factory):
        p1 = page_factory(active=True, created_by=self.user, updated_by=self.user)
        p2 = page_factory(active=False, created_by=self.user, updated_by=self.user)
        rv = self.runner.invoke(page_list, ['--active'])
        assert rv.exit_code == 0
        assert truncate_string(p1.title, 80) in rv.output
        assert truncate_string(p2.title, 80) not in rv.output

    def test_list_inactive_only(self, page_factory):
        p1 = page_factory(active=True, created_by=self.user, updated_by=self.user)
        p2 = page_factory(active=False, created_by=self.user, updated_by=self.user)
        rv = self.runner.invoke(page_list, ['--inactive'])
        assert rv.exit_code == 0
        assert truncate_string(p1.title, 80) not in rv.output
        assert truncate_string(p2.title, 80) in rv.output

    def test_create_ok_simple(self, mocker):
        title = 'Tytuł strony 1'
        fake_login = mocker.Mock(return_value=self.user)
        mocker.patch('bip.cli.pages.commands.login_user', fake_login)
        fake_edit = mocker.Mock(return_value=title)
        mocker.patch('bip.cli.pages.commands.click.edit', fake_edit)
        rv = self.runner.invoke(page_create, ['-t', title, '-u', self.user.name])
        assert f'strona {title} została utworzona' in rv.output

    def test_create_ok_no_description(self, mocker):
        title = 'Tytuł strony 1'
        mocker.patch(
            'bip.cli.pages.commands.login_user',
            mocker.Mock(return_value=self.user),
        )
        mocker.patch(
            'bip.cli.pages.commands.click.edit', mocker.Mock(return_value=title)
        )
        mocker.patch(
            'bip.cli.pages.commands.click.confirm', mocker.Mock(return_value=False)
        )
        rv = self.runner.invoke(page_create, ['-t', title, '-u', self.user.name])
        assert f'strona {title} została utworzona' in rv.output
        page = Page.get(Page.title == title)
        assert page.description is None

    def test_create_ok_with_description(self, mocker):
        title = 'Tytuł strony 1'
        text = 'Treść strony 1'
        description = 'Opis strony 1'
        mocker.patch(
            'bip.cli.pages.commands.login_user', mocker.Mock(return_value=self.user)
        )
        mocker.patch(
            'bip.cli.pages.commands.click.edit',
            mocker.Mock(side_effect=[text, description]),
        )
        mocker.patch(
            'bip.cli.pages.commands.click.confirm', mocker.Mock(return_value=True)
        )
        rv = self.runner.invoke(page_create, ['-t', title, '-u', self.user.name])
        assert f'strona {title} została utworzona' in rv.output
        page = Page.get(Page.title == title)
        assert page.text == text
        assert page.description == description

    def test_create_ok_with_labels(self, mocker, label_factory):
        label_a = 'Etykieta A'
        label_factory(name=label_a)
        label_b = 'Etykieta B'
        label_factory(name=label_b)
        title = 'Tytuł strony 1'
        text = 'Treść strony 1'
        description = 'Opis strony 1'
        mocker.patch(
            'bip.cli.pages.commands.login_user', mocker.Mock(return_value=self.user)
        )
        mocker.patch(
            'bip.cli.pages.commands.click.edit',
            mocker.Mock(side_effect=[text, description]),
        )
        mocker.patch(
            'bip.cli.pages.commands.click.confirm', mocker.Mock(return_value=True)
        )
        rv = self.runner.invoke(
            page_create,
            ['-t', title, '-u', self.user.name, '-l', label_a, '-l', label_b],
        )
        assert f'strona {title} została utworzona' in rv.output
        page = Page.get(Page.title == title)
        assert page.labels().count() == 2
        pagelabels = [x.label.name for x in page.labels()]
        assert all([label_a in pagelabels, label_b in pagelabels])

    def test_create_fail_no_text(self, mocker):
        title = 'Tytuł strony 1'
        mocker.patch(
            'bip.cli.pages.commands.login_user', mocker.Mock(return_value=self.user)
        )
        mocker.patch('bip.cli.pages.commands.click.edit', mocker.Mock(return_value=''))
        rv = self.runner.invoke(page_create, ['-t', title, '-u', self.user.name])
        assert rv.exit_code != 0
        assert 'Tekst strony jest wymagany' in rv.output

    def test_change_noop(self, mocker, page_factory):
        mocker.patch(
            'bip.cli.pages.commands.login_user', mocker.Mock(return_value=self.user)
        )
        page = page_factory(created_by=self.user, updated_by=self.user)
        rv = self.runner.invoke(page_change, ['-i', page.pk, '-u', self.user.name])
        assert 'nie wprowadzono żadnych zmian' in rv.output

    def test_change_title(self, mocker, page_factory):
        mocker.patch(
            'bip.cli.pages.commands.login_user', mocker.Mock(return_value=self.user)
        )
        title = 'Tytuł strony 1'
        page = page_factory(title=title, created_by=self.user, updated_by=self.user)
        new_title = 'Nowy tytuł'
        rv = self.runner.invoke(
            page_change, ['-i', page.pk, '-u', self.user.name, '-t', new_title]
        )
        assert 'została zmieniona' in rv.output
        page_obj = Page[page.pk]
        assert page_obj.title == new_title
        assert page_obj.slug == slugify(new_title)

    def test_change_active(self, mocker, page_factory):
        mocker.patch(
            'bip.cli.pages.commands.login_user', mocker.Mock(return_value=self.user)
        )
        page = page_factory(active=False, created_by=self.user, updated_by=self.user)
        rv = self.runner.invoke(
            page_change, ['-i', page.pk, '-u', self.user.name, '--active']
        )
        assert 'została zmieniona' in rv.output
        page_obj = Page[page.pk]
        assert page_obj.active is True

    def test_change_main(self, mocker, page_factory):
        actor = self.user
        mocker.patch(
            'bip.cli.pages.commands.login_user', mocker.Mock(return_value=actor)
        )
        page = page_factory(main=False, created_by=actor, updated_by=actor)
        rv = self.runner.invoke(
            page_change, ['-i', page.pk, '-u', actor.name, '--main']
        )
        assert 'została zmieniona' in rv.output
        page_obj = Page[page.pk]
        assert page_obj.main is True

    def test_change_order(self, mocker, page_factory):
        actor = self.user
        mocker.patch(
            'bip.cli.pages.commands.login_user', mocker.Mock(return_value=actor)
        )
        page = page_factory(created_by=actor, updated_by=actor)
        new_order = 2
        rv = self.runner.invoke(
            page_change, ['-i', page.pk, '-u', actor.name, '-o', str(new_order)]
        )
        assert 'została zmieniona' in rv.output
        page_obj = Page[page.pk]
        assert page_obj.order == new_order

    def test_labels_add_none(self, mocker, page_factory):
        actor = self.user
        mocker.patch(
            'bip.cli.pages.commands.login_user', mocker.Mock(return_value=actor)
        )
        page = page_factory(created_by=actor, updated_by=actor)
        rv = self.runner.invoke(
            page_labels, ['-i', page.pk, '-o', 'add', '-u', actor.name]
        )
        assert f'etykiety strony {page.title} nie zostały zmienione' in rv.output
        assert rv.exit_code == 0
        assert PageLabel.select().filter(PageLabel.page == page).count() == 0

    def test_labels_add_one(self, mocker, page_factory, label_factory):
        actor = self.user
        mocker.patch(
            'bip.cli.pages.commands.login_user', mocker.Mock(return_value=actor)
        )
        page = page_factory(created_by=actor, updated_by=actor)
        label = label_factory(name='etykieta 1')
        rv = self.runner.invoke(
            page_labels,
            ['-i', page.pk, '-o', 'add', '-u', actor.name, '-l', label.name],
        )
        assert rv.exit_code == 0
        assert f'etykiety strony {page.title} zostały zaktualizowane' in rv.output
        assert PageLabel.select().filter(PageLabel.page == page).count() == 1

    def test_labels_add_many(self, mocker, page_factory, label_factory):
        num_labels = 8
        actor = self.user
        mocker.patch(
            'bip.cli.pages.commands.login_user', mocker.Mock(return_value=actor)
        )
        page = page_factory(created_by=actor, updated_by=actor)
        labels = label_factory.create_batch(num_labels)
        call_args = ['-i', page.pk, '-o', 'add', '-u', actor.name]
        for label in labels:
            call_args.extend(['-l', label.name])
        rv = self.runner.invoke(page_labels, call_args)
        assert rv.exit_code == 0
        assert f'etykiety strony {page.title} zostały zaktualizowane' in rv.output
        assert PageLabel.select().filter(PageLabel.page == page).count() == num_labels

    def test_labels_replace_none(
                self, mocker, page_factory, label_factory, page_label_factory
            ):
        actor = self.user
        mocker.patch(
            'bip.cli.pages.commands.login_user', mocker.Mock(return_value=actor)
        )
        page = page_factory(created_by=actor, updated_by=actor)
        labels = label_factory.create_batch(2)
        for label in labels:
            page_label_factory(page=page, label=label)
        rv = self.runner.invoke(
            page_labels, ['-i', page.pk, '-o', 'replace', '-u', actor.name]
        )
        assert rv.exit_code == 0
        assert f'etykiety strony {page.title} zostały zaktualizowane' in rv.output
        assert PageLabel.select().filter(PageLabel.page == page).count() == 0

    def test_labels_replace_one(
                self, mocker, page_factory, label_factory, page_label_factory
            ):
        actor = self.user
        mocker.patch(
            'bip.cli.pages.commands.login_user', mocker.Mock(return_value=actor)
        )
        page = page_factory(created_by=actor, updated_by=actor)
        labels = label_factory.create_batch(2)
        for label in labels:
            page_label_factory(page=page, label=label)
        new_label = label_factory()
        rv = self.runner.invoke(
            page_labels,
            ['-i', page.pk, '-o', 'replace', '-u', actor.name, '-l', new_label.name]
        )
        assert rv.exit_code == 0
        assert f'etykiety strony {page.title} zostały zaktualizowane' in rv.output
        assert PageLabel.select().filter(PageLabel.page == page).count() == 1

    def test_labels_replace_many(
                self, mocker, page_factory, label_factory, page_label_factory
            ):
        actor = self.user
        mocker.patch(
            'bip.cli.pages.commands.login_user', mocker.Mock(return_value=actor)
        )
        page = page_factory(created_by=actor, updated_by=actor)
        labels = label_factory.create_batch(2)
        for label in labels:
            page_label_factory(page=page, label=label)
        new_label_count = 4
        new_labels = label_factory.create_batch(new_label_count)
        call_args = ['-i', page.pk, '-o', 'replace', '-u', actor.name]
        for label in new_labels:
            call_args.extend(['-l', label.name])
        rv = self.runner.invoke(page_labels, call_args)
        assert rv.exit_code == 0
        assert f'etykiety strony {page.title} zostały zaktualizowane' in rv.output
        assert PageLabel.select().filter(PageLabel.page == page).count() == new_label_count  # noqa: E501

    @pytest.mark.parametrize('abort', [False, True], ids=['continue', 'abort'])
    def test_labels_add_notfound_one_continue(
                self, mocker, page_factory, label_factory, page_label_factory, abort
            ):
        label_count = 2
        actor = self.user
        mocker.patch(
            'bip.cli.pages.commands.login_user', mocker.Mock(return_value=actor)
        )
        page = page_factory(created_by=actor, updated_by=actor)
        if abort:
            expected_msg = 'operacja zmiany etykiet strony przerwana'
        else:
            expected_msg = f'etykiety strony {page.title} nie zostały zmienione'
        labels = label_factory.create_batch(label_count)
        for label in labels:
            page_label_factory(page=page, label=label)
        new_label_name = 'dummy'
        call_args = ['-i', page.pk, '-o', 'add', '-u', actor.name, '-l', new_label_name]
        mocker.patch(
            'bip.cli.pages.commands.click.confirm', mocker.Mock(return_value=not abort)
        )
        rv = self.runner.invoke(page_labels, call_args)
        assert expected_msg in rv.output
        assert rv.exit_code == 0
        assert PageLabel.select().filter(PageLabel.page == page).count() == label_count


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
