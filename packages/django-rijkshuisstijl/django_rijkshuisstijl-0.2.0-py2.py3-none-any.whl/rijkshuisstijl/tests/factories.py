from datetime import timedelta

from django.utils import timezone

import factory.fuzzy
from rijkshuisstijl.tests.models import (
    Author,
    Award,
    Book,
    Company,
    Conference,
    Publisher,
)


class AuthorFactory(factory.django.DjangoModelFactory):
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    gender = factory.fuzzy.FuzzyChoice(("female", "male"))
    date_of_birth = factory.fuzzy.FuzzyDate(
        timezone.now().date() - timedelta(days=30), timezone.now().date() - timedelta(days=1)
    )
    slug = factory.Faker("uuid4")

    class Meta:
        model = Author


class AwardFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("name")
    author = factory.SubFactory(AuthorFactory)
    slug = factory.Faker("uuid4")

    class Meta:
        model = Award


class ConferenceFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("name")
    event_date = factory.Faker("date_object")

    class Meta:
        model = Conference


class CompanyFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("name")

    class Meta:
        model = Company


class PublisherFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("name")
    company = factory.SubFactory(CompanyFactory)

    class Meta:
        model = Publisher


class BookFactory(factory.django.DjangoModelFactory):
    publisher = factory.SubFactory(PublisherFactory)
    available = factory.Faker("pybool")
    avg_rating = factory.Faker("pydecimal", left_digits=1, right_digits=2)
    date_published = factory.fuzzy.FuzzyDateTime(
        timezone.now() - timedelta(days=30), timezone.now() - timedelta(days=1)
    )
    last_updated = factory.fuzzy.FuzzyDateTime(
        timezone.now() - timedelta(days=5), timezone.now() - timedelta(days=1)
    )
    stock = factory.Faker("pyint", min_value=5)
    title = factory.Faker("sentence")
    random_set = factory.Faker("sentence")

    @factory.post_generation
    def authors(self, create, extracted, **kwargs):
        authors = []

        if not create:
            return

        if extracted:
            authors = extracted

        for author in authors:
            self.authors.add(author)

    class Meta:
        model = Book
