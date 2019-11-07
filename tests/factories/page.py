import factory
from factory.alchemy import SQLAlchemyModelFactory

from bip.ext import db
from bip.models import Page

from .user import UserFactory


class PageFactory(SQLAlchemyModelFactory):

    title = factory.Faker('sentence', nb_words=4, locale='pl_PL')
    active = True
    text = factory.Faker('paragraph', locale='pl_PL')
    description = factory.Faker('paragraph', locale='pl_PL')
    created_by = factory.SubFactory(UserFactory, password='pass')

    class Meta:
        model = Page
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'flush'
