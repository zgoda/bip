from bip.data import directory
from bip.models import Directory

from . import DALTests


class TestDirectory(DALTests):

    def test_create_ok(self, user_factory, page_factory):
        user = user_factory(name='user1', password='user1', admin=True)
        page = page_factory(created_by=user)
        rv = directory.create(title='Directory 1', created_by=user, page=page)
        obj = Directory.query.get(rv.pk)
        assert obj == rv
