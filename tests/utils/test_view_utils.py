import pytest

from bip.utils.views import is_redirect_safe


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

    @pytest.mark.parametrize('params', [
        [LOCAL_HOST_URL, 'sftp://localhost:5000/some/where'],
        [LOCAL_HOST_URL, 'http://otherhost:5000/some/where'],
    ], ids=['scheme', 'netloc'])
    def test_not_safe(self, params, mocker):
        host_url, target = params
        fake_request = mocker.Mock(host_url=host_url)
        mocker.patch('bip.utils.views.request', fake_request)
        assert is_redirect_safe(target) is False
