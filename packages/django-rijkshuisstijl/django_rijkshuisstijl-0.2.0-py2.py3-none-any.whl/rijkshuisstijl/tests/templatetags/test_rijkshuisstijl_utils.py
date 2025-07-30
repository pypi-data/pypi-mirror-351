from unittest import skip
from django.test import TestCase
from django.utils.datetime_safe import date, datetime

from rijkshuisstijl.templatetags.rijkshuisstijl_utils import (
    format_value,
    get_field_label,
    get_recursed_field_label
)
from rijkshuisstijl.tests.factories import (
    AwardFactory,
    AuthorFactory,
    BookFactory,
    ConferenceFactory,
    PublisherFactory
)
from rijkshuisstijl.tests.models import Author, Award, Book, Conference, Publisher


class FormatValueTestCase(TestCase):
    def test_rh_display(self):
        publisher = PublisherFactory()
        publisher.rh_display_name = "Lorem ipsum"
        self.assertEqual(format_value(publisher, "name"), "Lorem ipsum")

    def test_get_display(self):
        publisher = PublisherFactory()
        publisher.get_name_display = lambda: "Lorem ipsum"

        self.assertEqual(format_value(publisher, "name"), "Lorem ipsum")

    def test___str__(self):
        publisher = PublisherFactory()
        self.assertEqual(format_value(publisher, "__str__"), str(publisher))

    def test_callable(self):
        publisher = PublisherFactory()
        book = Book.objects.create(publisher=publisher)
        publisher.name_fn = lambda: "Lorem ipsum"

        self.assertEqual(format_value(publisher, "name_fn"), "Lorem ipsum")
        self.assertEqual(format_value(book, "publisher__name_fn"), "Lorem ipsum")

    def test_none(self):
        self.assertEqual(format_value(""), "-")
        self.assertEqual(format_value("", "", "No value"), "No value")

        publisher = PublisherFactory()
        book = BookFactory(publisher=publisher)
        publisher.name_fn = lambda: ""

        self.assertEqual(format_value(publisher, "name_fn"), "-")
        self.assertEqual(format_value(book, "publisher__name_fn"), "-")

    def test_bool(self):
        publisher = PublisherFactory()
        book = BookFactory(publisher=publisher)

        publisher.bool = True
        self.assertIn("true.png", format_value(publisher, "bool"))
        self.assertIn("true.png", format_value(book, "publisher__bool"))

        publisher.bool = lambda: True
        self.assertIn("true.png", format_value(book, "publisher__bool"))

        publisher.bool = False
        self.assertIn("false.png", format_value(book, "publisher__bool"))

        publisher.bool = lambda: False
        self.assertIn("false.png", format_value(book, "publisher__bool"))

    def test_str(self):
        self.assertEqual(format_value("Lorem ipsum"), "Lorem ipsum")

        publisher = PublisherFactory()
        book = BookFactory(publisher=publisher)
        publisher.str = "Lorem ipsum"

        self.assertEqual(format_value(publisher, "str"), "Lorem ipsum")
        self.assertEqual(format_value(book, "publisher__str"), "Lorem ipsum")

    def test_manager(self):
        publisher = PublisherFactory()
        author_1 = AuthorFactory()
        author_2 = AuthorFactory()
        book = BookFactory(publisher=publisher)
        book.authors.set((author_1, author_2))

        self.assertEqual(format_value(book, "authors"), f"{str(author_1)}, {str(author_2)}")

    def test_iterable(self):
        publisher = PublisherFactory()
        book = BookFactory(publisher=publisher)
        publisher.iterable = ["Lorem", "ipsum"]

        self.assertEqual(format_value(publisher, "iterable"), "Lorem, ipsum")
        self.assertEqual(format_value(book, "publisher__iterable"), "Lorem, ipsum")

    def test_date(self):
        publisher = PublisherFactory()
        book = BookFactory(publisher=publisher)
        book.date_published = date(2020, 6, 29)
        self.assertEqual(format_value(book, "date_published"), date(2020, 6, 29))

    def test_datetime(self):
        publisher = PublisherFactory()
        book = BookFactory(publisher=publisher)
        book.date_published = datetime(2020, 6, 29)
        self.assertEqual(format_value(book, "date_published"), datetime(2020, 6, 29))

    def test_model_instance(self):
        publisher = PublisherFactory()
        publisher.get_absolute_url = lambda: "http://lorem.ipsum"
        self.assertEqual(
            format_value(publisher),
            f'<a class="link" href="http://lorem.ipsum">{publisher.name}</a>'
        )



class InstanceGetRecursedFieldLabelTestCase(TestCase):
    def test_verbose_name_field_label(self):
        """
        Test that verbose_name value will be returned from the given field_lookup
        """
        book = BookFactory()

        label = get_recursed_field_label(book, "random_set")

        self.assertEqual(label, "random set")

    def test_regex_fallback_field_label(self):
        """
        Test that dash formatted value will be returned from the given field_lookup
        which has no verbose_name
        """
        book = BookFactory()

        label = get_recursed_field_label(book, "last_updated")

        self.assertEqual(label, "last updated")

    def test_related_field_label(self):
        """
        Test that verbose_name will be returned from the given field_lookup
        which in this test is the name of a related (ForeignKey) field
        """
        book = BookFactory()

        label = get_recursed_field_label(book, "publisher")

        self.assertEqual(label, "publishing house")

    def test_related_field_verbose_name_fallback_label(self):
        """
        Test that verbose_name from the related model will be returned from the given
        field_lookup which in this test is the name of a related (ForeignKey) field
        """
        award = AwardFactory()

        label = get_recursed_field_label(award, "author")

        self.assertEqual(label, "Book author")

    def test_related_field_verbose_name_fallback_label_reverse(self):
        """
        Test that verbose_name_plural from the related model will be returned from
        the given field_lookup which in this test is the reverse name of a related
        (ForeignKey) field
        """
        instance = AuthorFactory()

        label = get_recursed_field_label(instance, "awards")

        self.assertEqual(label, "Awards")

    def test_related_field_verbose_name_plural_fallback_label(self):
        """
        Test that verbose_name_plural from the related model will be returned from
        the given field_lookup which in this test is the name of
        a related (ManyToManyField) field
        """
        book = BookFactory()

        label = get_recursed_field_label(book, "awards")

        self.assertEqual(label, "Awards")

    def test_related_field_regex_fallback_label(self):
        """
        Test that verbose_name of the field from the related model will be returned
        from the given field_lookup which in this test is the name of
        a related (ManyToManyField) field
        """
        publisher = PublisherFactory()

        label = get_recursed_field_label(publisher, "conferences__event_date")

        self.assertEqual(label, "event date")

    def test_related_field_lookup_label(self):
        """
        Test that verbose_name will be returned from the given field_lookup
        which in this test is a lookup string upon a related (ForeignKey) field
        """
        award = AwardFactory()

        label = get_recursed_field_label(award, "author__gender")

        self.assertEqual(label, "Gender")

    def test_related_field_lookup_same_field_label(self):
        """
        Test that verbose_name will be returned from the given field_lookup
        which in this test is a lookup string upon a related (ForeignKey) field.
        The field is the same on both models but only one of them is correct.
        """
        award = AwardFactory()

        label = get_recursed_field_label(award, "author__slug")

        self.assertEqual(label, "Author id")

    def test_related_field_lookup_regex_fallback_label(self):
        """
        Test that dash formatted value will be returned from the given field_lookup
        which in this test is a lookup string upon a related (ForeignKey) field
        """
        award = AwardFactory()

        label = get_recursed_field_label(award, "author__date_of_birth")

        self.assertEqual(label, "date of birth")

    def test_function(self):
        """
        Test that function will be called with the given object and the function's
        return value will be used as label
        """
        author = AuthorFactory(first_name="Henk")

        label = get_recursed_field_label(author, "get_name_label")

        self.assertEqual(label, "Foobar")

    def test_function_short_description(self):
        """
        Test that function's short_description will be returned
        """
        author = AuthorFactory(first_name="Henk")

        label = get_recursed_field_label(author, "get_slug_display")

        self.assertEqual(label, "Fancy slug label")

    def test_property(self):
        """
        Test that property will be called with the given object and the property's
        return value will be used as label
        """
        author = AuthorFactory()

        label = get_recursed_field_label(author, "label")

        self.assertEqual(label, "Author")

    def test_property_short_description(self):
        """
        Test that property's short_description will be returned
        """
        author = AuthorFactory()

        label = get_recursed_field_label(author, "first_name_localized")

        self.assertEqual(label, "Translated first name")

    def test_lookup_function(self):
        """
        Test that lookup function will be called with the given object
        """
        award = AwardFactory(author=AuthorFactory())

        label = get_recursed_field_label(award, "author__get_name_label")

        self.assertEqual(label, "Foobar")

    def test_lookup_function_short_description(self):
        """
        Test that lookup function's short_description will be returned
        """
        award = AwardFactory(author=AuthorFactory())

        label = get_recursed_field_label(award, "author__get_slug_display")

        self.assertEqual(label, "Fancy slug label")

    # Note this usecase will probably not happen, but testing expected behaviour
    # is preferred
    def test_many_to_many_property(self):
        """
        Test that many to many field property will fallback to regex fallback
        """
        publisher = PublisherFactory()

        label = get_recursed_field_label(publisher, "conferences__full_name")

        self.assertEqual(label, "full name")

    # Note this usecase will probably not happen, but testing expected behaviour
    # is preferred
    def test_many_to_many_property_short_description(self):
        """
        Test that many to many field property's short_description will be returned
        """
        publisher = PublisherFactory()

        label = get_recursed_field_label(publisher, "conferences__full_name_localized")

        self.assertEqual(label, "Localized full name")

    # Note this usecase will probably not happen, but testing expected behaviour
    # is preferred
    def test_many_to_many_function(self):
        """
        Test that many to many function will fallback to regex fallback
        """
        publisher = PublisherFactory()

        label = get_recursed_field_label(publisher, "conferences__get_days_until")

        self.assertEqual(label, "days until")

    # Note this usecase will probably not happen, but testing expected behaviour
    # is preferred
    def test_many_to_many_function_short_description(self):
        """
        Test that many to many function's short_description will be returned
        """
        publisher = PublisherFactory()

        label = get_recursed_field_label(publisher, "conferences__get_days_after")

        self.assertEqual(label, "Days after conference")


class QuerysetGetRecursedFieldLabelTestCase(TestCase):
    def test_verbose_name_field_label(self):
        """
        Test that verbose_name value will be returned from the given field_lookup
        """
        BookFactory.create_batch(size=3)

        label = get_recursed_field_label(Book.objects.all(), "random_set")

        self.assertEqual(label, "random set")

    def test_regex_fallback_field_label(self):
        """
        Test that dash formatted value will be returned from the given field_lookup
        which has no verbose_name
        """
        BookFactory.create_batch(size=3)

        label = get_recursed_field_label(Book.objects.all(), "last_updated")

        self.assertEqual(label, "last updated")

    def test_related_field_label(self):
        """
        Test that verbose_name will be returned from the given field_lookup
        which in this test is the name of a related (ForeignKey) field
        """
        BookFactory.create_batch(size=3)

        label = get_recursed_field_label(Book.objects.all(), "publisher")

        self.assertEqual(label, "publishing house")

    def test_related_field_verbose_name_fallback_label(self):
        """
        Test that verbose_name from the related model will be returned from the given
        field_lookup which in this test is the name of a related (ForeignKey) field
        """
        AwardFactory.create_batch(size=3)

        label = get_recursed_field_label(Award.objects.all(), "author")

        self.assertEqual(label, "Book author")

    def test_related_field_verbose_name_plural_fallback_label(self):
        """
        Test that verbose_name_plural from the related model will be returned from
        the given field_lookup which in this test is the name of
        a related (ManyToManyField) field
        """
        BookFactory.create_batch(size=3)

        label = get_recursed_field_label(Book.objects.all(), "awards")

        self.assertEqual(label, "Awards")

    def test_related_field_verbose_name_fallback_label_reverse(self):
        """
        Test that verbose_name_plural from the related model will be returned from
        the given field_lookup which in this test is the reverse name of a related
        (ForeignKey) field
        """
        AuthorFactory.create_batch(size=3)
        queryset = Author.objects.all()

        label = get_recursed_field_label(queryset, "awards")

        self.assertEqual(label, "Awards")

    def test_related_field_regex_fallback_label(self):
        """
        Test that verbose_name of the field from the related model will be returned
        from the given field_lookup which in this test is the name of
        a related (ManyToManyField) field
        """
        PublisherFactory.create_batch(size=3)

        label = get_recursed_field_label(
            Publisher.objects.all(), "conferences__event_date"
        )

        self.assertEqual(label, "event date")

    def test_related_field_lookup_label(self):
        """
        Test that verbose_name will be returned from the given field_lookup
        which in this test is a lookup string upon a related (ForeignKey) field
        """
        AwardFactory.create_batch(size=3)

        label = get_recursed_field_label(Award.objects.all(), "author__gender")

        self.assertEqual(label, "Gender")

    def test_related_field_lookup_same_field_label(self):
        """
        Test that verbose_name will be returned from the given field_lookup
        which in this test is a lookup string upon a related (ForeignKey) field.
        The field is the same on both models but only one of them is correct.
        """
        AwardFactory.create_batch(size=3)

        label = get_recursed_field_label(Award.objects.all(), "author__slug")

        self.assertEqual(label, "Author id")

    def test_related_field_lookup_regex_fallback_label(self):
        """
        Test that dash formatted value will be returned from the given field_lookup
        which in this test is a lookup string upon a related (ForeignKey) field
        """
        AwardFactory.create_batch(size=3)

        label = get_recursed_field_label(Award.objects.all(), "author__date_of_birth")

        self.assertEqual(label, "date of birth")

    # Note this usecase will probably not happen, but testing expected behaviour
    # is preferred
    def test_function(self):
        """
        Test that function will be called with the given object and the function's
        return value will be used as label
        """
        AuthorFactory.create_batch(size=3)
        queryset = Author.objects.all()

        label = get_recursed_field_label(queryset, "get_name_label")

        self.assertEqual(label, "name label")

    # Note this usecase will probably not happen, but testing expected behaviour
    # is preferred
    def test_function_short_description(self):
        """
        Test that the function's short_description will be returned
        """
        AuthorFactory.create_batch(size=3)
        queryset = Author.objects.all()

        label = get_recursed_field_label(queryset, "get_slug_display")

        self.assertEqual(label, "Fancy slug label")

    # Note this usecase will probably not happen, but testing expected behaviour
    # is preferred
    def test_property(self):
        """
        Test that property will be called with the given object and the property's
        return value will be used as label
        """
        AuthorFactory.create_batch(size=3)
        queryset = Author.objects.all()

        label = get_recursed_field_label(queryset, "label")

        self.assertEqual(label, "label")

    # Note this usecase will probably not happen, but testing expected behaviour
    # is preferred
    def test_property_short_description(self):
        """
        Test that property's short_description will be returned
        """
        AuthorFactory.create_batch(size=3)
        queryset = Author.objects.all()

        label = get_recursed_field_label(queryset, "first_name_localized")

        self.assertEqual(label, "Translated first name")

    # Note this usecase will probably not happen, but testing expected behaviour
    # is preferred
    def test_lookup_function(self):
        """
        Test that lookup function will be called with the given object
        """
        AwardFactory.create_batch(size=3)
        queryset = Award.objects.all()

        label = get_recursed_field_label(queryset, "author__get_name_label")

        self.assertEqual(label, "name label")

    # Note this usecase will probably not happen, but testing expected behaviour
    # is preferred
    def test_lookup_function_short_description(self):
        """
        Test that lookup function will return the function's short_description
        """
        AwardFactory.create_batch(size=3)
        queryset = Award.objects.all()

        label = get_recursed_field_label(queryset, "author__get_slug_display")

        self.assertEqual(label, "Fancy slug label")

    # Note this usecase will probably not happen, but testing expected behaviour
    # is preferred
    def test_many_to_many_property(self):
        """
        Test that many to many field property will fallback to regex fallback
        """
        PublisherFactory.create_batch(size=3)
        queryset = Publisher.objects.all()

        label = get_recursed_field_label(queryset, "conferences__full_name")

        self.assertEqual(label, "full name")

    # Note this usecase will probably not happen, but testing expected behaviour
    # is preferred
    def test_many_to_many_property_short_description(self):
        """
        Test that many to many field property's short_description will be used
        """
        PublisherFactory.create_batch(size=3)
        queryset = Publisher.objects.all()

        label = get_recursed_field_label(queryset, "conferences__full_name_localized")

        self.assertEqual(label, "Localized full name")

    # Note this usecase will probably not happen, but testing expected behaviour
    # is preferred
    def test_many_to_many_function(self):
        """
        Test that many to many field property will fallback to regex fallback
        """
        PublisherFactory.create_batch(size=3)
        queryset = Publisher.objects.all()

        label = get_recursed_field_label(queryset, "conferences__get_days_until")

        self.assertEqual(label, "days until")

    # Note this usecase will probably not happen, but testing expected behaviour
    # is preferred
    def test_many_to_many_function_short_description(self):
        """
        Test that many to many lookup function will use the short_description
        """
        PublisherFactory.create_batch(size=3)
        queryset = Publisher.objects.all()

        label = get_recursed_field_label(queryset, "conferences__get_days_after")

        self.assertEqual(label, "Days after conference")


class ClassGetRecursedFieldLabelTestCase(TestCase):
    def test_verbose_name_field_label(self):
        """
        Test that verbose_name value will be returned from the given field_lookup
        """
        label = get_recursed_field_label(Book, "random_set")

        self.assertEqual(label, "random set")

    def test_regex_fallback_field_label(self):
        """
        Test that dash formatted value will be returned from the given field_lookup
        which has no verbose_name
        """
        label = get_recursed_field_label(Book, "last_updated")

        self.assertEqual(label, "last updated")

    def test_related_field_label(self):
        """
        Test that verbose_name will be returned from the given field_lookup
        which in this test is the name of a related (ForeignKey) field
        """
        label = get_recursed_field_label(Book, "publisher")

        self.assertEqual(label, "publishing house")

    def test_related_field_verbose_name_fallback_label(self):
        """
        Test that verbose_name from the related model will be returned from the given
        field_lookup which in this test is the name of a related (ForeignKey) field
        """
        label = get_recursed_field_label(Award, "author")

        self.assertEqual(label, "Book author")

    def test_related_field_verbose_name_fallback_label_reverse(self):
        """
        Test that verbose_name_plural from the related model will be returned from
        the given field_lookup which in this test is the reverse name of a related
        (ForeignKey) field
        """
        label = get_recursed_field_label(Author, "awards")

        self.assertEqual(label, "Awards")

    def test_related_field_verbose_name_plural_fallback_label(self):
        """
        Test that verbose_name_plural from the related model will be returned from
        the given field_lookup which in this test is the name of
        a related (ManyToManyField) field
        """
        label = get_recursed_field_label(Book, "awards")

        self.assertEqual(label, "Awards")

    def test_related_field_regex_fallback_label(self):
        """
        Test that verbose_name of the field from the related model will be returned
        from the given field_lookup which in this test is the name of
        a related (ManyToManyField) field
        """
        label = get_recursed_field_label(Publisher, "conferences__event_date")

        self.assertEqual(label, "event date")

    def test_related_field_lookup_label(self):
        """
        Test that verbose_name will be returned from the given field_lookup
        which in this test is a lookup string upon a related (ForeignKey) field
        """
        label = get_recursed_field_label(Award, "author__gender")

        self.assertEqual(label, "Gender")

    def test_related_field_lookup_same_field_label(self):
        """
        Test that verbose_name will be returned from the given field_lookup
        which in this test is a lookup string upon a related (ForeignKey) field.
        The field is the same on both models but only one of them is correct.
        """
        label = get_recursed_field_label(Award, "author__slug")

        self.assertEqual(label, "Author id")

    def test_related_field_lookup_regex_fallback_label(self):
        """
        Test that dash formatted value will be returned from the given field_lookup
        which in this test is a lookup string upon a related (ForeignKey) field
        """
        label = get_recursed_field_label(Award, "author__date_of_birth")

        self.assertEqual(label, "date of birth")

    # Note this usecase will probably not happen, but testing expected behaviour
    # is preferred
    def test_function(self):
        """
        Test that function will be called with the given class and returns the
        regex fallback
        """
        label = get_recursed_field_label(Author, "get_name_label")

        self.assertEqual(label, "name label")

    # Note this usecase will probably not happen, but testing expected behaviour
    # is preferred
    def test_function_short_description(self):
        """
        Test that the function's short_description will be returned
        """
        label = get_recursed_field_label(Author, "get_slug_display")

        self.assertEqual(label, "Fancy slug label")

    # Note this usecase will probably not happen, but testing expected behaviour
    # is preferred
    def test_property(self):
        """
        Test that property will be called with the given class and the regex fallback
        will be used as label
        """
        label = get_recursed_field_label(Author, "label")

        self.assertEqual(label, "label")

    # Note this usecase will probably not happen, but testing expected behaviour
    # is preferred
    def test_property_short_description(self):
        """
        Test that property's short_description will be returned
        """
        label = get_recursed_field_label(Author, "first_name_localized")

        self.assertEqual(label, "Translated first name")

    # Note this usecase will probably not happen, but testing expected behaviour
    # is preferred
    def test_lookup_function(self):
        """
        Test that lookup function will be called with the given object
        """
        label = get_recursed_field_label(Award, "author__get_name_label")

        self.assertEqual(label, "name label")

    # Note this usecase will probably not happen, but testing expected behaviour
    # is preferred
    def test_many_to_many_property(self):
        """
        Test that many to many field property will fallback to regex fallback
        """
        label = get_recursed_field_label(Publisher, "conferences__full_name")

        self.assertEqual(label, "full name")

    # Note this usecase will probably not happen, but testing expected behaviour
    # is preferred
    def test_many_to_many_property_short_description(self):
        """
        Test that many to many field property's short_description will be returned
        """
        label = get_recursed_field_label(Publisher, "conferences__full_name_localized")

        self.assertEqual(label, "Localized full name")

    # Note this usecase will probably not happen, but testing expected behaviour
    # is preferred
    def test_many_to_many_function(self):
        """
        Test that many to many field function will fallback to regex fallback
        """
        label = get_recursed_field_label(Publisher, "conferences__get_days_until")

        self.assertEqual(label, "days until")

    # Note this usecase will probably not happen, but testing expected behaviour
    # is preferred
    def test_many_to_many_function_short_description(self):
        """
        Test that many to many field function's short_description will be returned
        """
        label = get_recursed_field_label(Publisher, "conferences__get_days_after")

        self.assertEqual(label, "Days after conference")


class ClassGetFieldLabelTestCase(TestCase):
    # field_lookup's
    def test_verbose_name_field_label(self):
        """
        Test that verbose_name value will be returned from the given field_lookup
        """
        label = get_field_label(Book, "random_set")

        self.assertEqual(label, "random set")

    def test_regex_fallback_field_label(self):
        """
        Test that dash formatted value will be returned from the given field_lookup
        which has no verbose_name
        """
        label = get_field_label(Book, "last_updated")

        self.assertEqual(label, "last updated")

    def test_related_field_label(self):
        """
        Test that verbose_name will be returned from the given field_lookup
        which in this test is the name of a related (ForeignKey) field
        """
        label = get_field_label(Book, "publisher")

        self.assertEqual(label, "publishing house")

    def test_related_field_verbose_name_fallback_label(self):
        """
        Test that verbose_name from the related model will be returned from the given
        field_lookup which in this test is the name of a related (ForeignKey) field
        """
        label = get_field_label(Award, "author")

        self.assertEqual(label, "Book author")

    def test_related_field_verbose_name_fallback_label_reverse(self):
        """
        Test that verbose_name_plural from the related model will be returned from
        the given field_lookup which in this test is the reverse name of a related
        (ForeignKey) field
        """
        label = get_field_label(Author, "awards")

        self.assertEqual(label, "Awards")

    def test_related_field_verbose_name_plural_fallback_label(self):
        """
        Test that verbose_name_plural from the related model will be returned from
        the given field_lookup which in this test is the name of
        a related (ManyToManyField) field
        """
        label = get_field_label(Book, "awards")

        self.assertEqual(label, "Awards")

    # Note this usecase will probably not happen, but testing expected behaviour
    # is preferred
    def test_function(self):
        """
        Test that function will be called with the given class and returns the
        regex fallback
        """
        label = get_field_label(Author, "get_name_label")

        self.assertEqual(label, "name label")

    # Note this usecase will probably not happen, but testing expected behaviour
    # is preferred
    def test_function_short_description(self):
        """
        Test that the function's short_description will be returned
        """
        label = get_field_label(Author, "get_slug_display")

        self.assertEqual(label, "Fancy slug label")

    # Note this usecase will probably not happen, but testing expected behaviour
    # is preferred
    def test_property(self):
        """
        Test that property will be called with the given class and the regex fallback
        will be used as label
        """
        label = get_field_label(Author, "label")

        self.assertEqual(label, "label")

    # Note this usecase will probably not happen, but testing expected behaviour
    # is preferred
    def test_property_short_description(self):
        """
        Test that property's short_description will be returned
        will be used as label
        """
        label = get_field_label(Author, "first_name_localized")

        self.assertEqual(label, "Translated first name")

    # Field instances
    def test_field_instance_verbose_name_field_label(self):
        """
        Test that verbose_name value will be returned from the given field_lookup
        """
        field = Book._meta.get_field("random_set")
        label = get_field_label(Book, field)

        self.assertEqual(label, "random set")

    def test_field_instance_regex_fallback_field_label(self):
        """
        Test that dash formatted value will be returned from the given field_lookup
        which has no verbose_name
        """
        field = Book._meta.get_field("last_updated")
        label = get_field_label(Book, field)

        self.assertEqual(label, "last updated")

    def test_field_instance_related_field_label(self):
        """
        Test that verbose_name will be returned from the given field_lookup
        which in this test is the name of a related (ForeignKey) field
        """
        field = Book._meta.get_field("publisher")
        label = get_field_label(Book, field)

        self.assertEqual(label, "publishing house")

    def test_field_instance_related_field_verbose_name_fallback_label(self):
        """
        Test that verbose_name from the related model will be returned from the given
        field_lookup which in this test is the name of a related (ForeignKey) field
        """
        field = Publisher._meta.get_field("company")
        label = get_field_label(Publisher, field)

        self.assertEqual(label, "Firm")

    def test_field_instance_related_field_verbose_name_plural_fallback_label(self):
        """
        Test that verbose_name_plural from the related model will be returned from
        the given field_lookup which in this test is the name of
        a related (ManyToManyField) field
        """
        field = Book._meta.get_field("awards")
        label = get_field_label(Book, field)

        self.assertEqual(label, "Awards")


class InstanceGetFieldLabelTestCase(TestCase):
    # field_lookup's
    def test_verbose_name_field_label(self):
        """
        Test that verbose_name value will be returned from the given field_lookup
        """
        label = get_field_label(BookFactory(), "random_set")

        self.assertEqual(label, "random set")

    def test_regex_fallback_field_label(self):
        """
        Test that dash formatted value will be returned from the given field_lookup
        which has no verbose_name
        """
        label = get_field_label(BookFactory(), "last_updated")

        self.assertEqual(label, "last updated")

    def test_related_field_label(self):
        """
        Test that verbose_name will be returned from the given field_lookup
        which in this test is the name of a related (ForeignKey) field
        """
        label = get_field_label(BookFactory(), "publisher")

        self.assertEqual(label, "publishing house")

    def test_related_field_verbose_name_fallback_label(self):
        """
        Test that verbose_name from the related model will be returned from the given
        field_lookup which in this test is the name of a related (ForeignKey) field
        """
        label = get_field_label(AwardFactory(), "author")

        self.assertEqual(label, "Book author")

    def test_related_field_verbose_name_fallback_label_reverse(self):
        """
        Test that verbose_name_plural from the related model will be returned from
        the given field_lookup which in this test is the reverse name of a related
        (ForeignKey) field
        """
        label = get_field_label(AuthorFactory(), "awards")

        self.assertEqual(label, "Awards")

    def test_related_field_verbose_name_plural_fallback_label(self):
        """
        Test that verbose_name_plural from the related model will be returned from
        the given field_lookup which in this test is the name of
        a related (ManyToManyField) field
        """
        label = get_field_label(BookFactory(), "awards")

        self.assertEqual(label, "Awards")

    def test_function(self):
        """
        Test that function will be called with the given instance and returns the
        regex fallback
        """
        label = get_field_label(AuthorFactory(), "get_name_label")

        self.assertEqual(label, "Foobar")

    def test_function_short_description(self):
        """
        Test that function's short_description will be returned
        """
        label = get_field_label(AuthorFactory(), "get_slug_display")

        self.assertEqual(label, "Fancy slug label")

    def test_property(self):
        """
        Test that property will be called with the given instance and the regex fallback
        will be used as label
        """
        label = get_field_label(AuthorFactory(), "label")

        self.assertEqual(label, "Author")

    def test_property_short_description(self):
        """
        Test that properties's short_description will be returned
        """
        label = get_field_label(AuthorFactory(), "first_name_localized")

        self.assertEqual(label, "Translated first name")

    # Field instances
    def test_field_instance_verbose_name_field_label(self):
        """
        Test that verbose_name value will be returned from the given field_lookup
        """
        field = Book._meta.get_field("random_set")
        label = get_field_label(BookFactory(), field)

        self.assertEqual(label, "random set")

    def test_field_instance_regex_fallback_field_label(self):
        """
        Test that dash formatted value will be returned from the given field_lookup
        which has no verbose_name
        """
        field = Book._meta.get_field("last_updated")
        label = get_field_label(BookFactory(), field)

        self.assertEqual(label, "last updated")

    def test_field_instance_related_field_label(self):
        """
        Test that verbose_name will be returned from the given field_lookup
        which in this test is the name of a related (ForeignKey) field
        """
        field = Book._meta.get_field("publisher")
        label = get_field_label(BookFactory(), field)

        self.assertEqual(label, "publishing house")

    def test_field_instance_related_field_verbose_name_fallback_label(self):
        """
        Test that verbose_name from the related model will be returned from the given
        field_lookup which in this test is the name of a related (ForeignKey) field
        """
        field = Publisher._meta.get_field("company")
        label = get_field_label(PublisherFactory(), field)

        self.assertEqual(label, "Firm")

    def test_field_instance_related_field_verbose_name_plural_fallback_label(self):
        """
        Test that verbose_name_plural from the related model will be returned from
        the given field_lookup which in this test is the name of
        a related (ManyToManyField) field
        """
        field = Book._meta.get_field("awards")
        label = get_field_label(BookFactory(), field)

        self.assertEqual(label, "Awards")
