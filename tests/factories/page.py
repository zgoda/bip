import factory
from factory.alchemy import SQLAlchemyModelFactory

from bip.ext import db
from bip.models import Page


class PageFactory(SQLAlchemyModelFactory):

    title = factory.Faker('sentence', nb_words=4, locale='pl_PL')
    active = True
    text = factory.Faker('paragraph', locale='pl_PL')
    description = factory.Faker('paragraph', locale='pl_PL')

    class Meta:
        model = Page
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'flush'
