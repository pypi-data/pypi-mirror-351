from django.core.paginator import Paginator
from django.template import Context, Template
from django.test import RequestFactory, TestCase

from rijkshuisstijl.tests.factories import AuthorFactory, BookFactory, PublisherFactory
from rijkshuisstijl.tests.models import Author, Book, Publisher
from rijkshuisstijl.tests.templatetags.utils import InclusionTagWebTest


class DatagridTestCase(InclusionTagWebTest):
    def setUp(self):
        self.tag = "datagrid"

        self.publisher_1 = PublisherFactory(name="Foo")
        self.publisher_2 = PublisherFactory(name="Bar")

        self.author_1 = AuthorFactory(first_name="John", last_name="Doe")
        self.author_2 = AuthorFactory(first_name="Joe", last_name="Average")

        self.book_1 = BookFactory(title="Lorem", publisher=self.publisher_1)
        self.book_1.authors.set((self.author_1,))

        self.book_2 = BookFactory(title="Ipsum", publisher=self.publisher_2)
        self.book_2.authors.set((self.author_2,))

        self.book_3 = BookFactory(title="Dolor", publisher=self.publisher_1)

    def template_render(self, config=None, data={}):
        config = config or {}
        config = Context({"config": config, "request": RequestFactory().get("/foo", data)})
        return Template("{% load rijkshuisstijl %}{% datagrid config=config %}").render(config)

    def test_render(self):
        self.assertTrue(self.template_render())

    def test_alternative_syntax(self):
        config = Context({"queryset": Book.objects.all(), "request": RequestFactory().get("/foo")})
        html = Template(
            '{% load rijkshuisstijl %}{% datagrid queryset=queryset columns="title,publisher__name:publisher name" orderable_columns="title,publisher__name" %}'
        ).render(config)

        self.assertInHTML(
            '<a class="datagrid__link" href="{}">{}</a>'.format("?ordering=title", "title"), html
        )
        self.assertInHTML(
            '<a class="datagrid__link" href="{}">{}</a>'.format(
                "?ordering=publisher__name", "name"
            ),
            html,
        )
        self.assertInHTML("Lorem", html)
        self.assertInHTML("Foo", html)
        self.assertInHTML("Dolor", html)
        self.assertInHTML("Bar", html)

    def test_class(self):
        html = self.template_render()
        self.assertIn('class="datagrid"', html)

    def test_id(self):
        html = self.template_render({"id": "my-first-datagrid"})
        self.assertIn("my-first-datagrid", html)

    def test_auto_id_uuid4(self):
        html = self.template_render()
        self.assertRegex(
            html, r"datagrid-[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}"
        )

    def test_no_results(self):
        html = self.template_render()
        self.assertInHTML("Geen resultaten", html)

    def test_columns(self):
        html = self.template_render({"columns": ("title", "publisher")})
        self.assertInHTML("title", html)
        self.assertInHTML("publisher", html)

    def test_rows(self):
        html = self.template_render(
            {"columns": ("title", "publisher"), "queryset": Book.objects.all()}
        )

        self.assertInHTML("Lorem", html)
        self.assertInHTML("Foo", html)
        self.assertInHTML("Dolor", html)
        self.assertInHTML("Bar", html)

    def test_filter(self):
        config = {
            "columns": ({"key": "title", "filter_label": "search title"}, "publisher"),
            "queryset": Book.objects.all(),
            "id": "my-first-datagrid",
            "filterable_columns": ["title"],
        }
        data = {"title": "m"}

        form = self.select_one("#datagrid-filter-form-my-first-datagrid", config, data)
        self.assertTrue(form)
        self.assertEqual(form.get("method"), "GET")

        filter_input = self.select_one("#datagrid-filter-title-my-first-datagrid", config, data)
        self.assertTrue(filter_input)
        self.assertEqual(filter_input.get("form"), "datagrid-filter-form-my-first-datagrid")
        self.assertEqual(filter_input.get("name"), "title")
        self.assertEqual(filter_input.get("value"), "m")
        self.assertEqual(filter_input.get("placeholder"), "search title")
        self.assertEqual(filter_input.get("type"), "search")

        html = self.render(config, data)
        self.assertInHTML("Lorem", html)
        self.assertInHTML("Ipsum", html)
        self.assertNotIn("Dolor", html)

    def test_filter_callable(self):
        config = {
            "columns": ("title", "publisher__get_absolute_url"),
            "queryset": Book.objects.all(),
            "id": "my-first-datagrid",
            "filterable_columns": ["publisher__get_absolute_url"],
        }
        data = {"publisher__get_absolute_url": self.publisher_2.get_absolute_url()}

        cells = self.select(".datagrid__cell", config, data)
        self.assertEqual(len(cells), 2)
        self.assertTextContent(
            ".datagrid__cell:nth-child(2)", self.publisher_2.get_absolute_url(), config, data
        )

    def test_filter_related(self):
        config = {
            "columns": ("title", {"key": "publisher"}),
            "queryset": Book.objects.all(),
            "filterable_columns": ["publisher"],
        }
        data = {"publisher": self.publisher_2.pk}
        rows = self.select(".datagrid__table-body .datagrid__row", config, data)
        self.assertEqual(len(rows), 1)
        self.assertTextContent(
            ".datagrid__table-body .datagrid__cell:first-child", self.book_2.title, config, data
        )

    def test_filter_filter_queryset(self):
        config = {
            "columns": ("title", {"key": "publisher"}),
            "queryset": Book.objects.all(),
            "filterable_columns": [{
                "key": "publisher",
                "filter_queryset": Publisher.objects.filter(name=self.publisher_1.name),
            }]
        }
        publisher_options = self.select("[name=\"publisher\"] option", config)

        self.assertEqual(len(publisher_options), 2)

        self.assertEqual(publisher_options[0].text, "---------")
        self.assertEqual(publisher_options[0]["value"], "")

        self.assertEqual(publisher_options[1].text, self.publisher_1.name)
        self.assertEqual(publisher_options[1]["value"], str(self.publisher_1.pk))

    def test_orderable_columns_list(self):
        """
        Configure the table headers for ordering using a list.
        """
        html = self.template_render(
            {
                "columns": ("title", {"key": "publisher__name", "label": "publisher name"}),
                "orderable_columns": ["title", "publisher__name"],
            }
        )

        self.assertInHTML(
            '<a class="datagrid__link" href="{}">{}</a>'.format("?ordering=title", "title"), html
        )
        self.assertInHTML(
            '<a class="datagrid__link" href="{}">{}</a>'.format(
                "?ordering=publisher__name", "publisher name"
            ),
            html,
        )

    def test_orderable_columns_dict(self):
        """
        Configure the table headers for ordering using a dict.
        """
        html = self.template_render(
            {
                "columns": ("title", "author"),
                "orderable_columns": {"title": "title", "author": "author__first_name"},
            }
        )

        self.assertInHTML(
            '<a class="datagrid__link" href="{}">{}</a>'.format("?ordering=title", "title"), html
        )
        self.assertInHTML(
            '<a class="datagrid__link" href="{}">{}</a>'.format(
                "?ordering=author__first_name", "author"
            ),
            html,
        )

    def test_order_asc(self):
        """
        Let the datagrid order the queryset (ascending).
        :return:
        """
        html = self.template_render(
            {
                "columns": ("title", "publisher"),
                "queryset": Book.objects.all(),
                "order": True,
                "orderable_columns": ("title", "publisher"),
                "ordering_key": "o",
            },
            {"o": "title"},
        )

        book_1_pos = html.find(str(self.book_1))
        book_2_pos = html.find(str(self.book_2))
        book_3_pos = html.find(str(self.book_3))

        self.assertLess(book_3_pos, book_2_pos)
        self.assertLess(book_2_pos, book_1_pos)

    def test_order_desc(self):
        """
        Let the datagrid order the queryset (descending).
        :return:
        """
        html = self.template_render(
            {
                "columns": ("title", "publisher"),
                "queryset": Book.objects.all(),
                "order": True,
                "orderable_columns": ("title", "publisher"),
                "ordering_key": "o",
            },
            {"o": "-title"},
        )

        book_1_pos = html.find(str(self.book_1))
        book_2_pos = html.find(str(self.book_2))
        book_3_pos = html.find(str(self.book_3))

        self.assertGreater(book_3_pos, book_2_pos)
        self.assertGreater(book_2_pos, book_1_pos)

    def test_no_pagination(self):
        """
        Don't paginate the datagrid.
        """
        paginator = Paginator(Book.objects.all(), 2)
        page_number = 1
        page_obj = paginator.page(page_number)

        html = self.template_render(
            {
                "columns": ("title", "publisher"),
                "queryset": Book.objects.all(),
                "is_paginated": False,
                "paginator": paginator,
                "page_number": page_number,
                "page_obj": page_obj,
            }
        )

        self.assertNotIn("paginator", html)

    def test_paginate(self):
        """
        Let the datagrid paginate the queryset/object list.
        """

        # QuerySet
        config = {
            "id": "my-first-datagrid",
            "columns": ("title", "publisher"),
            "queryset": Book.objects.all(),
            "paginate": True,
            "paginate_by": 2,
            "page_key": "p",
        }
        data = {"p": 2}
        html = self.render(config, data)

        self.assertNotIn(str(self.book_1), html)
        self.assertNotIn(str(self.book_2), html)
        self.assertIn(str(self.book_3), html)
        self.assertIn("paginator", html)

        input = self.select_one(".paginator .input", config, data)
        self.assertEqual(input.get("form"), "datagrid-paginator-form-my-first-datagrid")
        self.assertEqual(input.get("name"), "p")
        self.assertEqual(input.get("value"), "2")
        self.assertEqual(input.get("type"), "number")
        self.assertEqual(input.get("min"), "1")
        self.assertEqual(input.get("max"), "2")

        # object_list
        config = {
            "id": "my-first-datagrid",
            "columns": ("title", "publisher"),
            "object_list": [*Book.objects.all()],
            "paginate": True,
            "paginate_by": 2,
            "page_key": "p",
        }
        data = {"p": 2}
        html = self.render(config, data)

        self.assertNotIn(str(self.book_1), html)
        self.assertNotIn(str(self.book_2), html)
        self.assertIn(str(self.book_3), html)
        self.assertIn("paginator", html)
        self.assertIn("paginator", html)

        input = self.select_one(".paginator .input", config, data)
        self.assertEqual(input.get("form"), "datagrid-paginator-form-my-first-datagrid")
        self.assertEqual(input.get("name"), "p")
        self.assertEqual(input.get("value"), "2")
        self.assertEqual(input.get("type"), "number")
        self.assertEqual(input.get("min"), "1")
        self.assertEqual(input.get("max"), "2")

    def test_pagination(self):
        """
        Pass an external paginator.
        """
        paginator = Paginator(Book.objects.all(), 2)
        page_number = 2
        page_obj = paginator.page(page_number)

        config = {
            "id": "my-first-datagrid",
            "columns": ("title", "publisher"),
            "object_list": page_obj.object_list,
            "paginate": False,
            "is_paginated": True,
            "paginator": paginator,
            "page_key": "p",
            "page_number": page_number,
            "page_obj": page_obj,
        }

        html = self.render(config)

        self.assertNotIn(str(self.book_1), html)
        self.assertNotIn(str(self.book_2), html)
        self.assertIn(str(self.book_3), html)
        self.assertIn("paginator", html)
        self.assertIn("paginator", html)

        input = self.select_one(".paginator .input", config)
        self.assertEqual(input.get("form"), "datagrid-paginator-form-my-first-datagrid")
        self.assertEqual(input.get("name"), "p")
        self.assertEqual(input.get("type"), "number")
        self.assertEqual(input.get("min"), "1")
        self.assertEqual(input.get("max"), "2")

    def test_custom_presentation(self):
        html = self.template_render(
            {
                "columns": ("title", "authors"),
                "get_authors_display": lambda book: book.authors.first(),
                "queryset": Book.objects.all(),
            }
        )

        self.assertInHTML("Lorem", html)
        self.assertInHTML("John Doe", html)
        self.assertInHTML("Dolor", html)
        self.assertInHTML("Joe Average", html)

    def test_form(self):
        config = {
            "columns": ("title"),
            "queryset": Book.objects.all(),
            "id": "my-first-datagrid",
            "form": True,
            "form_action": "/foo",
            "form_buttons": [
                {"label": "Foo", "name": "Lorem", "icon_src": "data:image/png;base64,"},
                {
                    "class": "button--danger",
                    "label": "Bar",
                    "name": "Ipsum",
                    "icon_src": "data:image/png;base64,",
                },
            ],
            "form_checkbox_name": "bar",
        }

        self.assertSelector("#my-first-datagrid", config)

        form = self.select_one(".datagrid__form", config)
        self.assertIn("datagrid__form", form.get("class"))
        self.assertEqual(form.get("method"), "post")
        self.assertEqual(form.get("action"), "/foo")

        button_foo = self.select_one(".button", config)
        self.assertIn("button", button_foo.get("class"))
        self.assertIn("button--icon", button_foo.get("class"))
        # self.assertIn("button--small", button_foo.get("class"))
        # self.assertIn("button--transparent", button_foo.get("class"))
        self.assertNotIn("button--danger", button_foo.get("class"))
        self.assertEqual(button_foo.get("name"), "Lorem")
        self.assertEqual(button_foo.get("title"), "Foo")
        self.assertTrue(button_foo.select_one(".button__icon"))
        self.assertTrue(button_foo.select_one(".button__label"))

        button_bar = self.select_one(".button--danger", config)
        self.assertIn("button", button_bar.get("class"))
        self.assertIn("button--icon", button_bar.get("class"))
        # self.assertIn("button--small", button_bar.get("class"))
        self.assertNotIn("button--transparent", button_bar.get("class"))
        self.assertIn("button--danger", button_bar.get("class"))
        self.assertEqual(button_bar.get("name"), "Ipsum")
        self.assertEqual(button_bar.get("title"), "Bar")
        self.assertTrue(button_bar.select_one(".button__icon"))
        self.assertTrue(button_bar.select_one(".button__label"))

        select_all = self.select_one("#my-first-datagrid-select-all-top", config)
        self.assertIn("select-all", select_all.get("class"))
        self.assertEqual(select_all.get("type"), "checkbox")
        self.assertEqual(
            select_all.get("data-select-all"), '#my-first-datagrid .input[type="checkbox"]'
        )

        checkbox = self.select_one('.input[name="bar"][value="3"]', config)
        self.assertEqual(checkbox.get("type"), "checkbox")

    def test_toolbar_position_top(self):
        html = self.template_render(
            {
                "columns": ("title"),
                "queryset": Book.objects.all(),
                "id": "my-first-datagrid",
                "form": True,
                "form_buttons": [
                    {"label": "Foo", "name": "Lorem", "icon_src": "data:image/png;base64,"},
                    {
                        "class": "button--danger",
                        "label": "Bar",
                        "name": "Ipsum",
                        "icon_src": "data:image/png;base64,",
                    },
                ],
                "toolbar_position": "top",
            }
        )

        button_pos = html.find('class="button')
        table_body_pos = html.find('class="datagrid__table-body')

        self.assertGreater(button_pos, -1)
        self.assertGreater(table_body_pos, -1)

        self.assertLess(button_pos, table_body_pos)

    def test_toolbar_position_bottom(self):
        config = {
            "columns": ("title"),
            "queryset": Book.objects.all(),
            "id": "my-first-datagrid",
            "form": True,
            "form_buttons": [
                {"label": "Foo", "name": "Lorem", "icon_src": "data:image/png;base64,"},
                {
                    "class": "button--danger",
                    "label": "Bar",
                    "name": "Ipsum",
                    "icon_src": "data:image/png;base64,",
                },
            ],
            "toolbar_position": "bottom",
        }
        html = self.render(config)
        button_pos = html.find('class="button')
        table_body_pos = html.find('class="datagrid__table-body')

        self.assertGreater(button_pos, -1)
        self.assertGreater(table_body_pos, -1)

        self.assertGreater(button_pos, table_body_pos)

    def test_toolbar_position_both(self):
        html = self.template_render(
            {
                "columns": ("title"),
                "queryset": Book.objects.all(),
                "id": "my-first-datagrid",
                "form": True,
                "form_buttons": [
                    {"label": "Foo", "name": "Lorem", "icon_src": "data:image/png;base64,"},
                    {
                        "class": "button--danger",
                        "label": "Bar",
                        "name": "Ipsum",
                        "icon_src": "data:image/png;base64,",
                    },
                ],
                "toolbar_position": "both",
            }
        )

        button_pos_top = html.find('class="button')
        button_pos_bottom = html.rfind('class="button')
        table_body_pos = html.find('class="datagrid__table-body')
        self.assertGreater(button_pos_top, -1)
        self.assertGreater(button_pos_bottom, -1)
        self.assertGreater(table_body_pos, -1)

        self.assertLess(button_pos_top, table_body_pos)
        self.assertGreater(button_pos_bottom, table_body_pos)

    def test_modifier_key(self):
        config = {
            "columns": ("title", "publisher"),
            "queryset": Book.objects.all(),
            "modifier_key": "publisher",
            "modifier_column": "publisher",
            "modifier_mapping": {"Foo": "purple", "Bar": "violet"},
        }

        row_purple = self.select_one(".datagrid__row.datagrid__row--purple", config)
        self.assertTrue(row_purple)
        self.assertFalse(row_purple.select(".datagrid__cell.datagrid__cell--modifier:first-child"))
        self.assertTrue(row_purple.select(".datagrid__cell.datagrid__cell--modifier:last-child"))

        row_violet = self.select_one(".datagrid__row.datagrid__row--purple", config)
        self.assertTrue(row_violet)
        self.assertFalse(row_violet.select(".datagrid__cell.datagrid__cell--modifier:first-child"))
        self.assertTrue(row_violet.select(".datagrid__cell.datagrid__cell--modifier:last-child"))

    def test_get_absolute_url(self):
        self.book_1.get_absolute_url = lambda: "/foo"
        self.book_2.get_absolute_url = lambda: "/bar"

        html = self.template_render(
            {"columns": ("title", "publisher"), "object_list": [self.book_1, self.book_2]}
        )

        foo_html = 'href="/foo"'
        bar_html = 'href="/bar"'
        self.assertIn(foo_html, html)
        self.assertIn(bar_html, html)

    def test_url_reverse(self):
        html = self.template_render(
            {"columns": ("publisher"), "queryset": Book.objects.all(), "url_reverse": "detail"}
        )

        foo_html = 'href="/1"'
        bar_html = 'href="/2"'
        baz_html = 'href="/3"'
        self.assertIn(foo_html, html)
        self.assertIn(bar_html, html)
        self.assertIn(baz_html, html)

    def test_groups(self):
        config = {
            "columns": ["title"],
            "queryset": Book.objects.all(),
            "groups": {
                "lookup": "publisher__name",
                "groups": [
                    {"value": self.publisher_1.name, "label": "Publisher 1"},
                    {"value": self.publisher_2.name, "label": "Publisher 2"},
                ],
            },
        }

        captions = self.select(".datagrid__subtitle", config)

        self.assertEqual(captions[0].text, "Publisher 1")
        self.assertEqual(captions[1].text, "Publisher 2")

        groups = self.select(".datagrid__table-body", config)
        group_1_cells = groups[0].select(".datagrid__cell")
        group_2_cells = groups[1].select(".datagrid__cell")

        self.assertEqual(len(group_1_cells), 2)
        self.assertEqual(group_1_cells[0].text.strip(), "Lorem")
        self.assertEqual(group_1_cells[1].text.strip(), "Dolor")

        self.assertEqual(len(group_2_cells), 1)
        self.assertEqual(group_2_cells[0].text.strip(), "Ipsum")

    def test_groups_paginated(self):
        config = {
            "columns": ["title"],
            "queryset": Book.objects.all(),
            "groups": {
                "lookup": "publisher__name",
                "groups": [
                    {"value": self.publisher_1.name, "label": "Publisher 1"},
                    {"value": self.publisher_2.name, "label": "Publisher 2"},
                ],
            },
            "paginate": True,
            "paginate_by": 2,
        }

        cells = self.select(".datagrid__cell", config)
        self.assertEqual(len(cells), 2)

        result_count = self.select_one(".datagrid__result-count", config)
        self.assertEqual(result_count.text, "3 resultaten")

    def test_groups_callable(self):
        config = {
            "columns": ["title"],
            "queryset": Book.objects.all(),
            "groups": {
                "lookup": lambda b: b.publisher.name,
                "groups": [
                    {"value": self.publisher_1.name, "label": "Publisher 1"},
                    {"value": self.publisher_2.name, "label": "Publisher 2"},
                ],
            },
        }

        captions = self.select(".datagrid__subtitle", config)

        self.assertEqual(captions[0].text, "Publisher 1")
        self.assertEqual(captions[1].text, "Publisher 2")

        groups = self.select(".datagrid__table-body", config)
        group_1_cells = groups[0].select(".datagrid__cell")
        group_2_cells = groups[1].select(".datagrid__cell")

        self.assertEqual(len(group_1_cells), 2)
        self.assertEqual(group_1_cells[0].text.strip(), "Lorem")
        self.assertEqual(group_1_cells[1].text.strip(), "Dolor")

        self.assertEqual(len(group_2_cells), 1)
        self.assertEqual(group_2_cells[0].text.strip(), "Ipsum")

    def test_select(self):
        config = {
            "columns": ["title"],
            "queryset": Book.objects.all(),
            "form": True,
            "form_select": {"name": "My First Select"},
            "form_options": [
                {"label": "Foo", "value": "Bar", },
                {"label": "Lorem", "value": "Ipsum", },
            ],
        }

        select = self.select_one(".select", config)
        self.assertTrue(select)

        options = select.select(".select__option")
        self.assertEqual(len(options), 2)

        self.assertEqual(options[0].text, "Foo")
        self.assertEqual(options[0].get("value"), "Bar")

        self.assertEqual(options[1].text, "Lorem")
        self.assertEqual(options[1].get("value"), "Ipsum")

    def export_pdf_visible(self):
        config = {
            "columns": ["title"],
            "queryset": Book.objects.all(),
            "form": True,
            "export_buttons": ["pdf"],
        }
        self.assertSelector(".datagrid__export.datagrid__export--pdf", config)
