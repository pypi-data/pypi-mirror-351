from django.template import Context, Template
from django.test import RequestFactory

from bs4 import BeautifulSoup
from django_webtest import WebTest


class InclusionTagWebTest(WebTest):
    library = "rijkshuisstijl"

    def assertContext(self, config={}):
        context = self.call_function()
        self.assertTrue(context)

    def assertRender(self, config={}, data={}):
        html = self.render(config, data)
        self.assertTrue(html)

    def assertSelector(self, selector, config={}, data={}):
        node = self.select(selector, config, data)
        self.assertTrue(node)
        return node

    def assertNotSelector(self, selector, config={}, data={}):
        node = self.select(selector, config, data)
        self.assertFalse(node)
        return node

    def assertTextContent(self, selector, text, config={}, data={}):
        node = self.select_one(selector, config, data)
        self.assertEqual(str(text).strip(), node.text.strip())

    def render(self, config={}, data={}):
        config = config or {}
        context = Context({"config": config, "request": RequestFactory().get("/foo", data)})
        template = self.get_template(config)
        return template.render(context)

    def select_one(self, selector, config={}, data={}):
        html = self.render(config, data)
        soup = BeautifulSoup(html, features="lxml")
        return soup.select_one(selector)

    def select(self, selector, config={}, data={}):
        html = self.render(config, data)
        soup = BeautifulSoup(html, features="lxml")
        return soup.select(selector)

    def call_function(self, config={}):
        template = self.get_template(config)
        nodelist = template.compile_nodelist()
        inclusion_node = nodelist[1]
        function = inclusion_node.func
        return function(**config)

    def get_template(self, config={}):
        return Template("{% load " + self.library + " %}{% " + self.tag + " config=config %}")
