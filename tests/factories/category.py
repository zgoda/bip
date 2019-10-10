import factory
from factory.alchemy import SQLAlchemyModelFactory

from bip.ext import db
from bip.models import Category

from .directory import DirectoryFactory
from .page import PageFactory


class CategoryFactory(SQLAlchemyModelFactory):

    active = True
    title = factory.Faker('sentence', locale='pl_PL')
    description = factory.Faker('paragraph', locale='pl_PL')
    directory = factory.SubFactory(DirectoryFactory)
    page = factory.SubFactory(PageFactory)

    class Meta:
        model = Category
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'flush'
