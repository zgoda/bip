import pytest

from bip.models import User
from bip.utils.pagination import url_for_other_page, get_page, paginate


@pytest.mark.usefixtures('app')
class TestPaginationUtils:

    def test_url_for_other_page(self, mocker):
        other_page = 286
        fake_request = mocker.Mock(view_args={'p': 1}, endpoint='main.home')
        mocker.patch('bip.utils.pagination.request', fake_request)
        url = url_for_other_page(other_page)
        assert f'p={other_page}' in url

    def test_get_page_ok(self, mocker):
        page = 286
        fake_request = mocker.Mock(args={'p': str(page)})
        mocker.patch('bip.utils.pagination.request', fake_request)
        assert get_page() == page

    def test_get_page_no_param(self, mocker):
        fake_request = mocker.Mock(args={})
        mocker.patch('bip.utils.pagination.request', fake_request)
        assert get_page() == 1

    def test_get_page_wrong_param(self, mocker):
        fake_request = mocker.Mock(args={})
        mocker.patch('bip.utils.pagination.request', fake_request)
        assert get_page('page') == 1

    def test_get_page_wrong_value(self, mocker):
        fake_request = mocker.Mock(args={'p': 'invalid'})
        mocker.patch('bip.utils.pagination.request', fake_request)
        assert get_page() == 1

    @pytest.mark.parametrize('page', [2, 3])
    def test_paginate_defaults_middle_pages(
                self, page, user_factory, config, mocker
            ):
        mocker.patch('bip.utils.pagination.get_page', mocker.Mock(return_value=page))
        config['LIST_SIZE'] = 3
        user_factory.create_batch(10, password='pass')
        query = User.select()
        rv = paginate(query)
        assert rv.has_next is True
        assert rv.has_prev is True
        assert rv.per_page == config['LIST_SIZE']

    def test_paginate_defaults_first_page(self, user_factory, config, mocker):
        mocker.patch('bip.utils.pagination.get_page', mocker.Mock(return_value=1))
        config['LIST_SIZE'] = 3
        user_factory.create_batch(10, password='pass')
        query = User.select()
        rv = paginate(query)
        assert rv.has_next is True
        assert rv.has_prev is False

    def test_paginate_defaults_last_page(self, user_factory, config, mocker):
        mocker.patch('bip.utils.pagination.get_page', mocker.Mock(return_value=4))
        config['LIST_SIZE'] = 3
        user_factory.create_batch(10, password='pass')
        query = User.select()
        rv = paginate(query)
        assert rv.has_next is False
        assert rv.has_prev is True

    def test_paginate_custom_page(self, user_factory, config, mocker):
        mocker.patch('bip.utils.pagination.get_page', mocker.Mock(return_value=1))
        config['LIST_SIZE'] = 3
        user_factory.create_batch(10, password='pass')
        query = User.select()
        rv = paginate(query, page=4)
        assert rv.has_next is False
        assert rv.has_prev is True

    def test_paginate_custom_size(self, user_factory, config, mocker):
        mocker.patch('bip.utils.pagination.get_page', mocker.Mock(return_value=1))
        config['LIST_SIZE'] = 3
        user_factory.create_batch(10, password='pass')
        query = User.select()
        rv = paginate(query, size=20)
        assert rv.has_next is False
        assert rv.has_prev is False
