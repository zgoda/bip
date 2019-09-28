import factory
from factory.alchemy import SQLAlchemyModelFactory

from bip.ext import db
from bip.models import User


class UserFactory(SQLAlchemyModelFactory):

    name = factory.Faker('name')
    email = factory.Faker('email')
    password = factory.PostGenerationMethodCall('set_password')
    active = True
    admin = False

    class Meta:
        model = User
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'
