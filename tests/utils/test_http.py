from bip.utils.http import or_404


class TestHttpUtils:

    def test_none_object(self, mocker):
        fake_abort = mocker.Mock()
        mocker.patch('bip.utils.http.abort', fake_abort)
        or_404(None)
        fake_abort.assert_called_once_with(404)

    def test_non_none_object(self):
        obj = 'object'
        rv = or_404(obj)
        assert rv == obj
