import factory
from factory.alchemy import SQLAlchemyModelFactory

from bip.ext import db
from bip.models import Directory

from .user import UserFactory
from .page import PageFactory


class DirectoryFactory(SQLAlchemyModelFactory):

    active = True
    description = factory.Faker('paragraph', locale='pl_PL')
    created_by = factory.SubFactory(UserFactory)
    updated_by = factory.SubFactory(UserFactory)
    page = factory.SubFactory(PageFactory)

    class Meta:
        model = Directory
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'flush'
