from markdown import markdown
import factory
from factory import base

from bip.models import Page, User, db
from bip.utils.text import slugify

DEFAULT_PASSWORD = 'password'


class PeeweeOptions(base.FactoryOptions):
    def _build_default_options(self):
        return super(PeeweeOptions, self)._build_default_options() + [
            base.OptionDefault('database', None, inherit=True),
        ]


class PeeweeModelFactory(base.Factory):

    _options_class = PeeweeOptions

    class Meta:
        abstract = True

    @classmethod
    def _create(cls, target_class, *args, **kwargs):
        """Create an instance of the model, and save it to the database."""
        obj = target_class(**kwargs)
        obj.save()
        return obj

    @classmethod
    def _after_postgeneration(cls, instance, create, results=None):
        """Save again the instance if creating and at least one hook ran."""
        if create and results:
            # Some post-generation hooks ran, and may have modified us.
            instance.save()


class UserFactory(PeeweeModelFactory):

    class Meta:
        model = User
        database = db

    name = factory.Faker('name')
    email = factory.Faker('email', locale='pl_PL')
    password = DEFAULT_PASSWORD
    active = True
    admin = False


class PageFactory(PeeweeModelFactory):

    class Meta:
        model = Page
        database = db

    title = factory.Faker('sentence', nb_words=4, locale='pl_PL')
    active = True
    text = factory.Faker('paragraph', locale='pl_PL')
    description = factory.Faker('paragraph', locale='pl_PL')
    created_by = factory.SubFactory(UserFactory)

    @factory.lazy_attribute
    def slug(self):
        return slugify(self.title)

    @factory.lazy_attribute
    def text_html(self):
        return markdown(self.text)

    @factory.lazy_attribute
    def updated_by(self):
        return self.created_by
