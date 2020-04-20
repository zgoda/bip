import pytest

from bip.cli.pages.commands import page_change, page_create, page_list
from bip.models import Page
from bip.utils.text import slugify, truncate_string

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

    def test_create_ok_simple(self, mocker, user_factory):
        title = 'Tytuł strony 1'
        actor = user_factory(name=self.username, password=self.password)
        fake_login = mocker.Mock(return_value=actor)
        mocker.patch('bip.cli.pages.commands.login_user', fake_login)
        fake_edit = mocker.Mock(return_value=title)
        mocker.patch('bip.cli.pages.commands.click.edit', fake_edit)
        rv = self.runner.invoke(page_create, ['-t', title, '-u', actor.name])
        assert f'strona {title} została utworzona' in rv.output

    def test_create_ok_no_description(self, mocker, user_factory):
        title = 'Tytuł strony 1'
        actor = user_factory(name=self.username, password=self.password)
        mocker.patch(
            'bip.cli.pages.commands.login_user', mocker.Mock(return_value=actor)
        )
        mocker.patch(
            'bip.cli.pages.commands.click.edit', mocker.Mock(return_value=title)
        )
        mocker.patch(
            'bip.cli.pages.commands.click.confirm', mocker.Mock(return_value=False)
        )
        rv = self.runner.invoke(page_create, ['-t', title, '-u', actor.name])
        assert f'strona {title} została utworzona' in rv.output
        page = Page.get(Page.title == title)
        assert page.description is None

    def test_create_ok_with_description(self, mocker, user_factory):
        title = 'Tytuł strony 1'
        text = 'Treść strony 1'
        description = 'Opis strony 1'
        actor = user_factory(name=self.username, password=self.password)
        mocker.patch(
            'bip.cli.pages.commands.login_user', mocker.Mock(return_value=actor)
        )
        mocker.patch(
            'bip.cli.pages.commands.click.edit',
            mocker.Mock(side_effect=[text, description]),
        )
        mocker.patch(
            'bip.cli.pages.commands.click.confirm', mocker.Mock(return_value=True)
        )
        rv = self.runner.invoke(page_create, ['-t', title, '-u', actor.name])
        assert f'strona {title} została utworzona' in rv.output
        page = Page.get(Page.title == title)
        assert page.text == text
        assert page.description == description

    def test_create_ok_with_labels(self, mocker, user_factory, label_factory):
        label_a = 'Etykieta A'
        label_factory(name=label_a)
        label_b = 'Etykieta B'
        label_factory(name=label_b)
        title = 'Tytuł strony 1'
        text = 'Treść strony 1'
        description = 'Opis strony 1'
        actor = user_factory(name=self.username, password=self.password)
        mocker.patch(
            'bip.cli.pages.commands.login_user', mocker.Mock(return_value=actor)
        )
        mocker.patch(
            'bip.cli.pages.commands.click.edit',
            mocker.Mock(side_effect=[text, description]),
        )
        mocker.patch(
            'bip.cli.pages.commands.click.confirm', mocker.Mock(return_value=True)
        )
        rv = self.runner.invoke(
            page_create, ['-t', title, '-u', actor.name, '-l', label_a, '-l', label_b]
        )
        assert f'strona {title} została utworzona' in rv.output
        page = Page.get(Page.title == title)
        assert page.labels().count() == 2
        page_labels = [x.label.name for x in page.labels()]
        assert all([label_a in page_labels, label_b in page_labels])

    def test_create_fail_no_text(self, mocker, user_factory):
        title = 'Tytuł strony 1'
        actor = user_factory(name=self.username, password=self.password)
        mocker.patch(
            'bip.cli.pages.commands.login_user', mocker.Mock(return_value=actor)
        )
        mocker.patch('bip.cli.pages.commands.click.edit', mocker.Mock(return_value=''))
        rv = self.runner.invoke(page_create, ['-t', title, '-u', actor.name])
        assert rv.exit_code != 0
        assert 'Tekst strony jest wymagany' in rv.output

    def test_change_noop(self, mocker, user_factory, page_factory):
        actor = user_factory(name=self.username, password=self.password)
        mocker.patch(
            'bip.cli.pages.commands.login_user', mocker.Mock(return_value=actor)
        )
        page = page_factory()
        rv = self.runner.invoke(page_change, ['-i', page.pk, '-u', actor.name])
        assert 'nie wprowadzono żadnych zmian' in rv.output

    def test_change_title(self, mocker, user_factory, page_factory):
        actor = user_factory(name=self.username, password=self.password)
        mocker.patch(
            'bip.cli.pages.commands.login_user', mocker.Mock(return_value=actor)
        )
        title = 'Tytuł strony 1'
        page = page_factory(title=title)
        new_title = 'Nowy tytuł'
        rv = self.runner.invoke(
            page_change, ['-i', page.pk, '-u', actor.name, '-t', new_title]
        )
        assert 'została zmieniona' in rv.output
        page_obj = Page[page.pk]
        assert page_obj.title == new_title
        assert page_obj.slug == slugify(new_title)

    def test_change_active(self, mocker, user_factory, page_factory):
        actor = user_factory(name=self.username, password=self.password)
        mocker.patch(
            'bip.cli.pages.commands.login_user', mocker.Mock(return_value=actor)
        )
        page = page_factory(active=False)
        rv = self.runner.invoke(
            page_change, ['-i', page.pk, '-u', actor.name, '--active']
        )
        assert 'została zmieniona' in rv.output
        page_obj = Page[page.pk]
        assert page_obj.active is True

    def test_change_main(self, mocker, user_factory, page_factory):
        actor = user_factory(name=self.username, password=self.password)
        mocker.patch(
            'bip.cli.pages.commands.login_user', mocker.Mock(return_value=actor)
        )
        page = page_factory(main=False)
        rv = self.runner.invoke(
            page_change, ['-i', page.pk, '-u', actor.name, '--main']
        )
        assert 'została zmieniona' in rv.output
        page_obj = Page[page.pk]
        assert page_obj.main is True

    def test_change_order(self, mocker, user_factory, page_factory):
        actor = user_factory(name=self.username, password=self.password)
        mocker.patch(
            'bip.cli.pages.commands.login_user', mocker.Mock(return_value=actor)
        )
        page = page_factory()
        new_order = 2
        rv = self.runner.invoke(
            page_change, ['-i', page.pk, '-u', actor.name, '-o', str(new_order)]
        )
        assert 'została zmieniona' in rv.output
        page_obj = Page[page.pk]
        assert page_obj.order == new_order
