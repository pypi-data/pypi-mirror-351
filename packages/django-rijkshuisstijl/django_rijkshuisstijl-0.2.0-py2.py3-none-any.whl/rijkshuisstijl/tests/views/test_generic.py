from django.test import RequestFactory, TestCase
from django.urls import reverse_lazy

from rijkshuisstijl.views.generic import (
    CreateView,
    DeleteMultipleView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from rijkshuisstijl.tests.models import Author, Award, Book, Publisher
from rijkshuisstijl.tests.factories import AuthorFactory, AwardFactory, BookFactory, PublisherFactory


class ViewTestCaseMixin:
    url_name = ""

    def client_get(self, url_name=None, kwargs=None, method="get", get_params={}):
        url_name = url_name if url_name else self.url_name

        if not kwargs:
            try:
                kwargs = {"pk": self.object.pk}
            except AttributeError:
                kwargs = None

        url = reverse_lazy(url_name, kwargs=kwargs)

        if get_params:
            url = url + "?" + get_params

        return getattr(self.client, method.lower())(url)

    def test_200(self):
        response = self.client_get()
        self.assertEqual(response.status_code, 200)

    def test_template_base(self):
        response = self.client_get()
        self.assertTemplateUsed(response, template_name="rijkshuisstijl/views/abstract/master.html")
        self.assertTemplateUsed(response, template_name="rijkshuisstijl/views/abstract/base.html")

    def test_script(self):
        response = self.client_get()
        self.assertContains(response, "rh-js.js")

    def test_css(self):
        response = self.client_get()
        self.assertContains(response, "rh-css.css")


class FormTestCaseMixin:
    def setUp(self):
        PublisherFactory()
        AuthorFactory()

    def client_get_form(self, fields):
        kwargs = {"model": Book, "fields": fields}

        factory = RequestFactory()
        request = factory.get("/foo")
        view = self.view.as_view(**kwargs)

        try:
            return view(request, pk=self.object.pk)
        except AttributeError:
            return view(request)

    def test_template(self):
        response = self.client_get()
        self.assertTemplateUsed(response, template_name="rijkshuisstijl/views/abstract/form.html")

    def test_context_default(self):
        response = self.client_get()
        context = response.context_data.get("form_config")

        self.assertEqual(context.get("label"), "Verzenden")
        self.assertEqual(context.get("status"), "info")
        self.assertEqual(context.get("title"), None)
        self.assertEqual(context.get("text"), None)
        self.assertEqual(context.get("wysiwyg"), None)

    def test_context_custom(self):
        kwargs = {
            "model": Book,
            "fields": ("title",),
            "label": "lorem ipsum",
            "status": "warning",
            "title": "foo",
            "text": "bar",
            "wysiwyg": "<p>baz</p>",
        }

        factory = RequestFactory()
        request = factory.get("/foo")
        view = self.view.as_view(**kwargs)

        try:
            response = view(request, pk=self.object.pk)
        except AttributeError:
            response = view(request)

        context = response.context_data.get("form_config")

        self.assertEqual(context.get("label"), "lorem ipsum")
        self.assertEqual(context.get("status"), "warning")
        self.assertEqual(context.get("title"), "foo")
        self.assertEqual(context.get("text"), "bar")
        self.assertEqual(context.get("wysiwyg"), "<p>baz</p>")

    def test_method(self):
        response = self.client_get()
        self.assertContains(response, 'method="post"')

    def test_enctype(self):
        response = self.client_get()
        self.assertContains(response, 'enctype="multipart/form-data"')

    def test_fields_visible(self):
        response = self.client_get_form(
            (
                "authors",
                "publisher",
                "available",
                "date_published",
                "last_updated",
                "stock",
                "title",
            )
        )
        form = response.context_data.get("form")

        for field_name in form._meta.fields:
            self.assertContains(response, 'name="{}"'.format(field_name))

    def test_fields_invisible(self):
        response = self.client_get_form(("title",))
        self.assertNotContains(response, 'name="{}"'.format("available"))

    def test_boolean_field(self):
        response = self.client_get_form(("available",))
        self.assertContains(response, 'type="{}"'.format("checkbox"))

    def test_decimal_field(self):
        response = self.client_get_form(("avg_rating",))
        self.assertContains(response, 'type="{}"'.format("number"))

    def test_date_field(self):
        response = self.client_get_form(("date_published",))
        self.assertContains(response, 'type="{}"'.format("date"))

    def test_datetime_field(self):
        response = self.client_get_form(("last_updated",))
        self.assertContains(response, 'type="{}"'.format("text"))

    def test_integer_field(self):
        response = self.client_get_form(("stock",))
        self.assertContains(response, 'type="{}"'.format("number"))

    def test_submit(self):
        response = self.client_get_form([])
        self.assertContains(response, 'type="{}"'.format("submit"))


class TemplateViewTestCase(ViewTestCaseMixin, TestCase):
    url_name = "template"
    view = TemplateView

    def test_context_default(self):
        response = self.client_get()
        context = response.context_data.get("textbox_config")

        self.assertEqual(context.get("status"), None)
        self.assertEqual(context.get("title"), None)
        self.assertEqual(context.get("text"), None)
        self.assertEqual(context.get("wysiwyg"), None)

    def test_context_custom(self):
        kwargs = {"status": "success", "title": "foo", "text": "bar", "wysiwyg": "<p>baz</p>"}

        factory = RequestFactory()
        request = factory.get("/foo")
        view = self.view.as_view(**kwargs)
        response = view(request)
        context = response.context_data.get("textbox_config")

        self.assertEqual(context.get("status"), "success")
        self.assertEqual(context.get("title"), "foo")
        self.assertEqual(context.get("text"), "bar")
        self.assertEqual(context.get("wysiwyg"), "<p>baz</p>")

    def test_template(self):
        response = self.client_get()
        self.assertTemplateUsed(
            response, template_name="rijkshuisstijl/views/generic/template.html"
        )

    def test_components(self):
        response = self.client_get()
        self.assertTemplateUsed(
            response, template_name="rijkshuisstijl/components/textbox/textbox.html"
        )


class CreateViewTestCase(ViewTestCaseMixin, FormTestCaseMixin, TestCase):
    url_name = "create"
    view = CreateView

    def test_template(self):
        response = self.client_get()
        self.assertTemplateUsed(response, template_name="rijkshuisstijl/views/generic/create.html")

    def test_components(self):
        response = self.client_get()
        self.assertTemplateUsed(response, template_name="rijkshuisstijl/components/form/form.html")


class DetailViewTestCase(ViewTestCaseMixin, TestCase):
    url_name = "detail"
    view = DetailView

    def setUp(self):
        self.publisher = PublisherFactory()
        self.author = AuthorFactory()
        self.object = BookFactory(publisher=self.publisher)
        self.object.authors.set((self.author,))

    def test_context_default(self):
        response = self.client_get()
        context_toolbar = response.context_data.get("toolbar_config")
        context_key_value_table = response.context_data.get("key_value_table_config")

        self.assertEqual(context_toolbar, None)

        self.assertEqual(context_key_value_table.get("class"), "key-value-table--justify")
        self.assertEqual(context_key_value_table.get("object"), self.object)
        self.assertEqual(
            context_key_value_table.get("fields"),
            ("title", "authors", "publisher", "date_published", "stock", "random_set"),
        )

    def test_context_custom(self):
        author = self.author

        class View(self.view):
            def get_object(self):
                return author

        kwargs = {"fields": ("first_name", "last_name"), "model": Author}

        factory = RequestFactory()
        request = factory.get("/foo")

        view = View.as_view(**kwargs)

        response = view(request)
        context = response.context_data.get("key_value_table_config")

        self.assertEqual(context.get("fields"), ("first_name", "last_name"))
        self.assertEqual(context.get("object"), self.author)

    def test_template(self):
        response = self.client_get()
        self.assertTemplateUsed(response, template_name="rijkshuisstijl/views/generic/detail.html")

    def test_components(self):
        response = self.client_get()
        self.assertTemplateUsed(
            response, template_name="rijkshuisstijl/components/title-header/title-header.html"
        )
        self.assertTemplateUsed(
            response, template_name="rijkshuisstijl/components/key-value-table/key-value-table.html"
        )

    def test_toolbar(self):
        book = self.object

        class View(self.view):
            def get_object(self):
                return book

        kwargs = {
            "fields": ("title",),
            "model": Book,
            "toolbar_config": {
                "items": [
                    {
                        "href": "#",
                        "label": "Foo",
                        "title": "Bar",
                        "icon_src": "data:image/png;base64",
                    }
                ]
            },
        }

        factory = RequestFactory()
        request = factory.get("/foo")

        view = View.as_view(**kwargs)

        response = view(request)
        self.assertContains(response, "toolbar")

    def test_fields_visible(self):
        response = self.client_get()
        fields = ("title", "writers", "publishing house", "date published", "stock")
        for field in fields:
            self.assertContains(response, field)

    def test_fields_invisible(self):
        response = self.client_get()
        self.assertNotContains(response, "last updated")
        self.assertNotContains(response, "last_updated")

    def test_foreign_key(self):
        response = self.client_get()

        model_field = Book._meta.get_field("publisher")

        self.assertContains(response, model_field.verbose_name)
        self.assertContains(response, str(self.object.publisher))

    def test_reverse_foreign_key_field(self):
        kwargs = {"pk": self.publisher.pk}
        url_name = "publisher-detail"

        books = [
            BookFactory(title="Jungle Book", publisher=self.publisher),
            BookFactory(title="Pinkeltje", publisher=self.publisher),
            BookFactory(title="Harry Potter", publisher=self.publisher),
        ]

        response = self.client_get(url_name=url_name, kwargs=kwargs)

        expected_book_value = ", ".join([str(book) for book in books])
        expected_book_label = "book set"

        self.assertContains(response, expected_book_value)
        self.assertContains(response, expected_book_label)

    def test_reverse_related_name_field(self):
        kwargs = {"pk": self.author.pk}
        url_name = "author-detail"

        awards = [
            AwardFactory(name="Book of the year 2012", author=self.author),
            AwardFactory(name="Book of the decade 2020", author=self.author),
            AwardFactory(name="Book of the century 1900", author=self.author),
        ]

        response = self.client_get(url_name=url_name, kwargs=kwargs)

        expected_award_value = ", ".join([str(award) for award in awards])
        expected_award_label = Award._meta.verbose_name_plural

        self.assertContains(response, expected_award_value)
        self.assertContains(response, expected_award_label)

    def test_many_to_many(self):
        AuthorFactory(first_name="James", last_name="Bond"),
        AuthorFactory(first_name="John", last_name="Doe"),

        authors = Author.objects.all()

        expected_authors_value = ", ".join(
            [f"{author.first_name} {author.last_name}" for author in authors]
        )

        self.object.authors.set(authors)

        model_field = Book._meta.get_field("authors")

        response = self.client_get()

        self.assertContains(response, expected_authors_value)
        self.assertContains(response, model_field.verbose_name)

    def test_reverse_many_to_many(self):
        kwargs = {"pk": self.author.pk}
        url_name = "author-book-detail"

        books = [
            BookFactory(title="Lord Of The Rings", publisher=self.publisher),
            BookFactory(title="The Witcher", publisher=self.publisher),
        ]

        self.author.book_set.set(books)

        response = self.client_get(url_name=url_name, kwargs=kwargs)

        expected_book_value = ", ".join([str(book) for book in books])
        expected_book_label = "book set"

        self.assertContains(response, expected_book_value)
        self.assertContains(response, expected_book_label)

    def test_set_field_without_relation(self):
        response = self.client_get()

        model_field = Book._meta.get_field("random_set")

        self.assertContains(response, model_field.verbose_name)
        self.assertContains(response, self.object.random_set)


class ListViewTestCase(ViewTestCaseMixin, TestCase):
    url_name = "list"
    view = ListView

    def setUp(self):
        self.publisher_1 = PublisherFactory(name="foo")
        self.publisher_2 = PublisherFactory(name="bar")

        self.author_1 = AuthorFactory(first_name="John", last_name="Doe")
        self.author_2 = AuthorFactory(first_name="Joe", last_name="Average")

        self.book_1 = BookFactory(title="Lorem", publisher=self.publisher_1)
        self.book_1.authors.set((self.author_1,))

        self.book_2 = BookFactory(title="Ipsum", publisher=self.publisher_2)
        self.book_2.authors.set((self.author_2,))

        self.book_3 = BookFactory(title="Dolor", publisher=self.publisher_1)
        self.book_3.authors.set((self.author_1, self.author_2))

    def test_context_default(self):
        response = self.client_get()
        context = response.context_data.get("datagrid_config")

        self.assertEqual(
            context.get("columns"),
            ("title", "authors", "publisher", "date_published", "stock", "random_set"),
        )
        self.assertEqual(context.get("queryset")[0], self.book_1)
        self.assertEqual(context.get("queryset")[1], self.book_2)
        self.assertEqual(context.get("queryset")[2], self.book_3)
        self.assertEqual(context.get("modifier_key"), None)
        self.assertEqual(context.get("modifier_column"), None)
        self.assertEqual(context.get("ordering_key"), "ordering")

    def test_template(self):
        response = self.client_get()
        self.assertTemplateUsed(response, template_name="rijkshuisstijl/views/generic/list.html")

    def test_components(self):
        response = self.client_get()
        self.assertTemplateUsed(
            response, template_name="rijkshuisstijl/components/datagrid/datagrid.html"
        )

    def test_paginator(self):
        response = self.client_get()
        self.assertContains(response, "paginator")

    def test_fields_visible(self):
        response = self.client_get()
        fields = ("title", "authors", "publisher", "date published", "stock")
        for field in fields:
            self.assertContains(response, field)

    def test_fields_invisible(self):
        response = self.client_get()
        self.assertNotContains(response, "last updated")
        self.assertNotContains(response, "last_updated")

    def test_empty(self):
        Book.objects.all().delete()
        response = self.client_get()
        object_list = response.context_data.get("object_list")
        self.assertEqual(len(object_list), 0)

    def test_urlize_override(self):
        """
        Tests that setting urlize on a column basis overrides datagrid's global urlize
        """
        self.view.columns = [{"key": "name"}, {"key": "company", "urlize": False}]

        response = self.client_get(url_name="publisher-list")

        companies = (self.publisher_1.company, self.publisher_2.company,)

        for company in companies:
            with self.subTest(company=company):
                self.assertContains(
                    response,
                    f'<a class="link" href="{company.get_absolute_url()}">{company}</a>'
                )


class UpdateViewTestCase(ViewTestCaseMixin, FormTestCaseMixin, TestCase):
    url_name = "update"
    view = UpdateView

    def setUp(self):
        self.publisher = PublisherFactory()
        self.author = AuthorFactory()
        self.object = BookFactory(publisher=self.publisher)
        self.object.authors.set((self.author,))

    def test_template(self):
        response = self.client_get()
        self.assertTemplateUsed(response, template_name="rijkshuisstijl/views/generic/update.html")

    def test_components(self):
        response = self.client_get()
        self.assertTemplateUsed(response, template_name="rijkshuisstijl/components/form/form.html")


class DeleteViewTestCase(ViewTestCaseMixin, TestCase):
    url_name = "delete"
    view = DeleteView

    def setUp(self):
        self.publisher = PublisherFactory()
        self.object = BookFactory(publisher=self.publisher)

    def test_template(self):
        response = self.client_get()
        self.assertTemplateUsed(response, template_name="rijkshuisstijl/views/generic/delete.html")

    def test_components(self):
        response = self.client_get()
        self.assertTemplateUsed(response, template_name="rijkshuisstijl/components/form/form.html")

    def test_confirm(self):
        response = self.client_get(kwargs={"pk": self.object.pk})

        self.assertContains(
            response,
            f"U staat op het punt om {self.object} te verwijderen, weet u het zeker?"
        )
        self.assertEqual(Book.objects.first(), self.object)

    def test_delete(self):
        response = self.client_get(kwargs={"pk": self.object.pk}, method="post")
        self.assertRedirects(response, "/")
        self.assertEqual(Book.objects.first(), None)


class DeleteMultipleViewTestCase(ViewTestCaseMixin, TestCase):
    url_name = "delete-multiple"
    view = DeleteMultipleView

    def setUp(self):
        self.publisher = PublisherFactory()
        self.object_1 = BookFactory(publisher=self.publisher)
        self.object_2 = BookFactory(publisher=self.publisher)
        self.object_3 = BookFactory(publisher=self.publisher)

    def test_template(self):
        response = self.client_get()
        self.assertTemplateUsed(response, template_name="rijkshuisstijl/views/generic/delete.html")

    def test_components(self):
        response = self.client_get()
        self.assertTemplateUsed(response, template_name="rijkshuisstijl/components/form/form.html")

    def test_confirm(self):
        response = self.client_get(get_params=f"pk={self.object_1.pk}&pk={self.object_3.pk}")
        self.assertContains(
            response, "U staat op het punt om 2 boeken te verwijderen, weet u het zeker?"
        )
        self.assertEqual(Book.objects.first(), self.object_1)
        self.assertEqual(len(Book.objects.all()), 3)

    def test_delete(self):
        response = self.client_get(
            get_params=f"pk={self.object_1.pk}&pk={self.object_3.pk}", method="post"
        )
        self.assertRedirects(response, "/")
        self.assertEqual(Book.objects.first(), self.object_2)
        self.assertEqual(len(Book.objects.all()), 1)
