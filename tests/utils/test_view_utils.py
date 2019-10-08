from flask import url_for

import pytest

from bip.utils.views import is_redirect_safe, next_redirect


class TestSafeRedirect:

    LOCAL_HOST_URL = 'http://localhost:5000'

    @pytest.mark.parametrize('target', [
        '/some/where',
        f'{LOCAL_HOST_URL}/some/where/else'
    ], ids=['relative', 'absolute'])
    def test_safe(self, target, mocker):
        fake_request = mocker.Mock(host_url=self.LOCAL_HOST_URL)
        mocker.patch('bip.utils.views.request', fake_request)
        assert is_redirect_safe(target)

    @staticmethod
    @pytest.mark.parametrize('params', [
        [LOCAL_HOST_URL, 'sftp://localhost:5000/some/where'],
        [LOCAL_HOST_URL, 'http://otherhost:5000/some/where'],
    ], ids=['scheme', 'netloc'])
    def test_not_safe(params, mocker):
        host_url, target = params
        fake_request = mocker.Mock(host_url=host_url)
        mocker.patch('bip.utils.views.request', fake_request)
        assert is_redirect_safe(target) is False


@pytest.mark.usefixtures('app')
class TestNextRedirect:

    LOCAL_HOST_URL = 'http://localhost:5000'
    FALLBACK_ENDPOINT = 'auth.login'

    def test_only_fallback(self):
        assert next_redirect(self.FALLBACK_ENDPOINT) == url_for(self.FALLBACK_ENDPOINT)

    def test_all_valid(self, mocker):
        u1 = '/some/where'
        u2 = '/other/place'
        fake_request = mocker.Mock(args={'next': u1}, host_url=self.LOCAL_HOST_URL)
        fake_session = {'next': u2}
        mocker.patch('bip.utils.views.request', fake_request)
        mocker.patch('bip.utils.views.session', fake_session)
        assert next_redirect(self.FALLBACK_ENDPOINT) == u1

    def test_2nd_valid(self, mocker):
        u1 = 'ftp://localhost:5000/some/where'
        u2 = '/other/place'
        fake_request = mocker.Mock(args={'next': u1}, host_url=self.LOCAL_HOST_URL)
        fake_session = {'next': u2}
        mocker.patch('bip.utils.views.request', fake_request)
        mocker.patch('bip.utils.views.session', fake_session)
        assert next_redirect(self.FALLBACK_ENDPOINT) == u2

    def test_all_invalid(self, mocker):
        u1 = 'ftp://localhost:5000/some/where'
        u2 = 'http://othersite/other/place'
        fake_request = mocker.Mock(args={'next': u1}, host_url=self.LOCAL_HOST_URL)
        fake_session = {'next': u2}
        mocker.patch('bip.utils.views.request', fake_request)
        mocker.patch('bip.utils.views.session', fake_session)
        assert next_redirect(self.FALLBACK_ENDPOINT) == url_for(self.FALLBACK_ENDPOINT)
