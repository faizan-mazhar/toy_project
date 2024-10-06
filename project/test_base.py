from django.test import TestCase
import factory
from faker import Faker

from user.models import Writer
from article.models import Article

fake = Faker()


class TestBase(TestCase):

    def setUp(self) -> None:
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()

    def get_writer(self, authenticate=False, writer_dict={}):

        writer = WriterFactory(**writer_dict)

        if authenticate:
            self.client.force_login(writer)

        return writer

    def get_editor(self, authenticate=False, editor_dict={}):
        editor_dict["is_editor"] = True
        return self.get_writer(authenticate=authenticate,
                               writer_dict=editor_dict)


class ArticleFactory(factory.django.DjangoModelFactory):
    """Article model factory class"""

    class Meta:
        model = Article


class WriterFactory(factory.django.DjangoModelFactory):
    """Writer model factory class"""

    class Meta:
        model = Writer

    name = factory.LazyFunction(fake.name)
    # Generate unique email by appending timestamp and random number
    email = factory.LazyFunction(
        lambda: f"{fake.email().split('@')[0]}@example.com"
    )

    # Set username to be the same as the email
    username = factory.LazyAttribute(lambda o: o.email)
    is_superuser = False
    first_name = factory.LazyFunction(fake.first_name)
    last_name = factory.LazyFunction(fake.last_name)
