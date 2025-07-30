from django import template
from django.conf import settings
from django.shortcuts import resolve_url
from django.template.base import TextNode
from django.template.loader import render_to_string
from django.templatetags.static import static
from django.urls import NoReverseMatch
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from rijkshuisstijl.templatetags.rijkshuisstijl import register

from .rijkshuisstijl_helpers import (
    get_id,
    get_request_user,
    merge_config,
    parse_arg,
    parse_kwarg,
)


@register.tag("row")
def row(parser, token):
    children = parser.parse(("endrow",))
    parser.delete_first_token()
    return ParentNode(token, children, "rijkshuisstijl/components/row/row.html")


@register.inclusion_tag("rijkshuisstijl/components/card/card.html")
def card(**kwargs):
    """
    Renders a card.

    Example:

        {% card config=config %}
        {% card option1='foo' option2='bar' %}

    Available options:

        - class: Optional, a string with additional CSS classes.
        - title: Optional, Title to show.
        - text: Optional, Text to show.
        - wysiwyg: Optional, Raw HTML to be shown, styled automatically.
        - urlize: Optional, if True text is passed to "urlize" template filter, automatically creating hyperlinks.
        - urlize_target: Optional, "target" attribute for links generated using "urlize".

    :param config:
    """
    config = merge_config(kwargs)

    def get_wysiwyg():
        wysiwyg = config.get("wysiwyg")
        if wysiwyg:
            return mark_safe(wysiwyg)

    def get_button_config():
        href = config.get("button_href")

        if not href:
            return None

        return {
            "class": config.get("button_class"),
            "far_icon": config.get("button_far_icon"),
            "fas_icon": config.get("button_fas_icon"),
            "href": href,
            "label": config.get("button_label"),
        }

    # kwargs
    config["class"] = config.get("class", None)
    config["close"] = parse_kwarg(config, "close", False)
    config["id"] = get_id(config, "textbox")
    config["status"] = config.get("status", None)
    config["title"] = config.get("title", None)
    config["text"] = config.get("text", None)
    config["wysiwyg"] = get_wysiwyg()
    config["urlize"] = config.get("urlize", True)
    config["urlize_target"] = config.get("urlize_target")
    config["button_config"] = get_button_config()

    config["config"] = config
    return config


@register.inclusion_tag("rijkshuisstijl/components/footer/footer.html", takes_context=True)
def footer(context, **kwargs):
    """
    Renders a page footer which may contain (django-sitetree) navigation. Use "footer" as the sitetree alias.

    Example:

        {% footer config=config %}
        {% footer option1='foo' option2='bar' %}

    Available options:

        - class: Optional, a string with additional CSS classes.

    :param context:
    :param kwargs:
    """
    kwargs = merge_config(kwargs)

    # kwargs
    kwargs["class"] = kwargs.get("class", None)

    kwargs["request"] = context["request"]

    kwargs["config"] = kwargs
    return kwargs


@register.inclusion_tag("rijkshuisstijl/components/header/header.html")
def header(**kwargs):
    """
    Renders a page header.

    Example:

        {% header config=config %}
        {% header option1='foo' option2='bar' %}

    Available options:

        - class: Optional, a string with additional CSS classes.
        - hide_mobile_menu_button: Optional, a bool, if True, hides the toggle menu button.
        - logo_src: Optional, a string to containing the logo url.
        - logo_mobile_src: Optional, a string to containing the mobile logo url.

    :param kwargs:
    """
    kwargs = merge_config(kwargs)

    # kwargs
    kwargs["class"] = kwargs.get("class", None)
    kwargs["logo_src"] = kwargs.get(
        "logo_src", static("rijkshuisstijl/components/logo/logo-tablet.svg")
    )
    kwargs["logo_mobile_src"] = kwargs.get(
        "logo_mobile_src", static("rijkshuisstijl/components/logo/logo-mobile.svg")
    )
    kwargs["hide_mobile_menu_button"] = kwargs.get("hide_mobile_menu_button", False)

    kwargs["config"] = kwargs
    return kwargs


@register.inclusion_tag("rijkshuisstijl/components/hero/hero.html")
def hero(**kwargs):
    """
    Renders an hero image.

    Example:

        {% hero config=config %}
        {% hero option1='foo' option2='bar' %}

    Available options:

        - alt: Required, The alt text for the image.
        - src: Required, The url to the image (see mobile_src, tablet_src and laptop src).

        - mobile_src: Optional, Specifies an image url specific to mobile screen sizes.
        - tablet_src: Optional, Specifies an image url specific to tablet screen sizes.
        - laptop_src: Optional, Specifies an image url specific to laptop screen sizes.
        - class: Optional, a string with additional CSS classes.
        - width: Optional, Sets the width attribute on the image.
        - height: Optional, Sets the height attribute on the image.
        - hide_on_error: Optional, if true, hides the image (visibility: hidden) when loading fails.
        - href: Optional, an optional url to link to.
        - title: Optional, Shows title as text in the hero.
        - body: Optional, Shows body as text in the hero.
    """
    config = merge_config(kwargs)
    config["alt"] = config.get("alt", "")
    config["src"] = config.get("src", "")
    config["mobile_src"] = config.get("mobile_src", None)
    config["tablet_src"] = config.get("tablet_src", None)
    config["laptop_src"] = config.get("laptop_src", None)
    config["class"] = ("hero " + config.get("class", "")).strip()
    config["width"] = config.get("width", None)
    config["height"] = config.get("height", None)
    config["hide_on_error"] = config.get("hide_on_error", False)
    config["href"] = config.get("href", "")
    config["title"] = config.get("title")
    config["body"] = config.get("body")
    config["config"] = config

    config["image_config"] = config.copy()
    config["image_config"].pop("class")
    return config


@register.inclusion_tag("rijkshuisstijl/components/image/image.html")
def image(**kwargs):
    """
    Renders an image.

    Example:

        {% image config=config %}
        {% image option1='foo' option2='bar' %}

    Available options:

        - alt: Required, The alt text for the image.
        - src: Required, The url to the image (see mobile_src, tablet_src and laptop src).

        - class: Optional, a string with additional CSS classes.
        - href: Optional, an optional url to link to.
        - mobile_src: Optional, Specifies an image url specific to mobile screen sizes.
        - tablet_src: Optional, Specifies an image url specific to tablet screen sizes.
        - laptop_src: Optional, Specifies an image url specific to laptop screen sizes.
        - width: Optional, Sets the width attribute on the image.
        - height: Optional, Sets the height attribute on the image.
        - hide_on_error: Optional, if true, hides the image (visibility: hidden) when loading fails.


    :param kwargs:
    """
    kwargs = merge_config(kwargs)
    kwargs["alt"] = kwargs.get("alt", "")
    kwargs["class"] = kwargs.get("class", None)
    kwargs["href"] = kwargs.get("href", "")
    kwargs["src"] = kwargs.get("src", "")
    kwargs["mobile_src"] = kwargs.get("mobile_src", None)
    kwargs["tablet_src"] = kwargs.get("tablet_src", None)
    kwargs["laptop_src"] = kwargs.get("laptop_src", None)
    kwargs["width"] = kwargs.get("width", None)
    kwargs["height"] = kwargs.get("height", None)
    kwargs["hide_on_error"] = kwargs.get("hide_on_error", False)

    kwargs["config"] = kwargs
    return kwargs


@register.inclusion_tag("rijkshuisstijl/components/intro/intro.html")
def intro(**kwargs):
    """
    Renders an intro.

    Example:

        {% intro config=config %}
        {% intro option1='foo' option2='bar' %}

    Available options:

        - class: Optional, a string with additional CSS classes.
        - status: Optional, A status string from the Django messages framework, styling the textbox accordingly.
        - title: Optional, Title to show.
        - text: Optional, Text to show.
        - wysiwyg: Optional, Raw HTML to be shown, styled automatically.
        - urlize: Optional, if True text is passed to "urlize" template filter, automatically creating hyperlinks.
        - urlize_target: Optional, "target" attribute for links generated using "urlize".


    :param kwargs:
    """
    config = merge_config(kwargs)

    def get_wysiwyg():
        wysiwyg = config.get("wysiwyg")
        if wysiwyg:
            return mark_safe(wysiwyg)

    # kwargs
    config["class"] = config.get("class", None)
    config["title"] = config.get("title", None)
    config["status"] = config.get("status", None)
    config["text"] = config.get("text", None)
    config["wysiwyg"] = get_wysiwyg()
    config["urlize"] = config.get("urlize", True)
    config["urlize_target"] = config.get("urlize_target")

    config["config"] = config
    return config


@register.inclusion_tag("rijkshuisstijl/components/login-bar/login-bar.html", takes_context=True)
def login_bar(context, **kwargs):
    """
    Renders a login bar.

    Example:

        {% login_bar config=config %}
        {% login_bar option1='foo' option2='bar' %}

    Available options:

        - details_url: Required, The url to link to when the username is clicked.
        - logout_url: Required, The url to link to when the logout link is clicked.
        - login_url: Required, The url to link to when the login link is clicked.
        - registration_url: Required, The url to link to when the register link is clicked.

        - class: Optional, a string with additional CSS classes.
        - admin_link: Optional, If true and user is staff, creates link to admin.
        - label_login: Optional, alternative label for the login link.
        - label_logged_in_as: Optional, alternative label for the logged in as label.
        - label_logout: Optional, alternative label for the logout link.
        - label_request_account: Optional, alternative label for the registration link.
        - label_admin: Optional, alternative label for the admin link.


    :param context:
    :param kwargs:
    """
    config = merge_config(kwargs)

    # i18n
    config["label_login"] = config.get("label_login", _("Inloggen"))
    config["label_logged_in_as"] = config.get("label_logged_in_as", _("Ingelogd als"))
    config["label_logout"] = config.get("label_logout", _("Uitloggen"))
    config["label_request_account"] = config.get("label_request_account", _("Account aanvragen"))
    config["label_admin"] = config.get("label_admin", _("Beheer"))

    # kwargs
    try:
        config["details_url"] = config.get(
            "details_url", resolve_url(getattr(settings, "LOGIN_REDIRECT_URL", ""))
        )
    except NoReverseMatch:
        config["details_url"] = None

    try:
        config["logout_url"] = config.get(
            "logout_url", resolve_url(getattr(settings, "LOGOUT_URL", ""))
        )
    except NoReverseMatch:
        config["logout_url"] = None

    try:
        config["login_url"] = config.get(
            "login_url", resolve_url(getattr(settings, "LOGIN_URL", ""))
        )
    except NoReverseMatch:
        config["login_url"] = None

    try:
        config["registration_url"] = config.get(
            "registration_url", resolve_url(getattr(settings, "REGISTRATION_URL", ""))
        )
    except NoReverseMatch:
        config["registration_url"] = None

    config["class"] = config.get("class")
    config["admin_link"] = config.get("admin_link", False)

    config["request"] = context["request"]
    config["config"] = config
    return config


@register.inclusion_tag("rijkshuisstijl/components/logo/logo.html")
def logo(**kwargs):
    """
    Renders the logo.

    Example:

        {% logo config=config %}
        {% logo option1='foo' option2='bar' %}

    Available options:

        - alt: Required, The alt text for the image.
        - src: Required, The url to the image (see mobile_src).
        - mobile_src: Required, Specifies an image url specific to mobile screen sizes.

        - class: Optional, a string with additional CSS classes.


    :param kwargs:
    """
    kwargs = merge_config(kwargs)

    # kwargs
    kwargs["alt"] = kwargs.get("alt", _("Logo Rijksoverheid"))
    kwargs["src"] = kwargs.get("src", static("rijkshuisstijl/components/logo/logo-tablet.svg"))
    kwargs["mobile_src"] = kwargs.get(
        "mobile_src", static("rijkshuisstijl/components/logo/logo-mobile.svg")
    )

    kwargs["config"] = kwargs
    return kwargs


@register.inclusion_tag(
    "rijkshuisstijl/components/navigation-bar/navigation-bar.html", takes_context=True
)
def navigation_bar(context, **kwargs):
    """
    Renders a navigation bar which may contain (django-sitetree) navigation. Use "navigation-bar" as the sitetree alias.

    Example:

        {% navigation_bar config=config %}
        {% navigation_bar option1='foo' option2='bar' %}

    Available options:

        - details_url: Required, The url to link to when the username is clicked.
        - logout_url: Required, The url to link to when the logout link is clicked.
        - login_url: Required, The url to link to when the login link is clicked.
        - registration_url: Required, The url to link to when the register link is clicked.

        - class: Optional, a string with additional CSS classes.
        - label_login: Optional, alternative label for the login link.
        - label_logged_in_as: Optional, alternative label for the logged in as label.
        - label_logout: Optional, alternative label for the logout link.
        - label_request_account: Optional, alternative label for the registration link.
        - search_url: Optional, The url to send the search query to, setting no url (default) disables search.
        - search_placeholder: Optional, alternative label to show as search input placeholder.
        - search_method: Optional, The method to use for the search form.
        - search_name: Optional, The method to use for the search input.
        - show_breadcrumbs: Optional, If True (default) breadcrumbs will be shown.


    :param context:
    :param kwargs:
    """
    kwargs = merge_config(kwargs)

    # i18n
    kwargs["label_login"] = kwargs.get("label_login", _("Inloggen"))
    kwargs["label_logged_in_as"] = kwargs.get("label_logged_in_as", _("Ingelogd als"))
    kwargs["label_logout"] = kwargs.get("label_logout", _("Uitloggen"))
    kwargs["label_request_account"] = kwargs.get("label_request_account", _("Account aanvragen"))

    # kwargs
    kwargs["details_url"] = kwargs.get(
        "details_url", resolve_url(getattr(settings, "LOGIN_REDIRECT_URL", "#/"))
    )
    kwargs["logout_url"] = kwargs.get(
        "logout_url", resolve_url(getattr(settings, "LOGOUT_URL", "#/"))
    )
    kwargs["login_url"] = kwargs.get("login_url", resolve_url(getattr(settings, "LOGIN_URL", "#/")))
    kwargs["registration_url"] = kwargs.get(
        "registration_url", resolve_url(getattr(settings, "REGISTRATION_URL", "#/"))
    )
    kwargs["search_url"] = kwargs.get("search_url", None)
    kwargs["search_placeholder"] = kwargs.get("search_placeholder", _("Zoeken"))
    kwargs["search_method"] = kwargs.get("search_method", "get")
    kwargs["search_name"] = kwargs.get("search_name", "q")

    kwargs["show_breadcrumbs"] = kwargs.get("show_breadcrumbs", True)

    kwargs["request"] = context["request"]
    kwargs["user"] = get_request_user(context["request"])
    kwargs["config"] = kwargs
    return kwargs


@register.inclusion_tag("rijkshuisstijl/components/search/search.html", takes_context=True)
def search(context, **kwargs):
    """
    Renders a search form.

    Example:

        {% search config=config %}
        {% search option1='foo' option2='bar' %}

    Available options:

        - action: Required, The url to send the search query to.

        - class: Optional, a string with additional CSS classes.
        - label_placeholder: Optional, alternative label to show as placeholder.
        - name: Optional, The method to use for the search input, defaults to 'query'.
        - method: Optional, The method to use for the search form, defaults to 'GET'.


    :param context:
    :param kwargs:
    """
    kwargs = merge_config(kwargs)
    request = context["request"]

    # kwargs
    kwargs["action"] = kwargs.get("action", "")
    kwargs["class"] = kwargs.get("class", None)
    kwargs["method"] = kwargs.get("method", "GET")
    kwargs["name"] = kwargs.get("name", "query")
    kwargs["label_placeholder"] = kwargs.get("label_placeholder", _("Zoeken"))

    request_dict = getattr(request, str(kwargs["method"]).upper(), {})
    kwargs["value"] = request_dict.get(kwargs["name"], "")

    kwargs["request"] = context["request"]
    kwargs["config"] = kwargs

    return kwargs


@register.inclusion_tag("rijkshuisstijl/components/skiplink/skiplink.html")
def skiplink(**kwargs):
    """
    Renders a skiplink (jump to content) for screen readers.
    Should be used with skiplink_target.

    Example:

        {% skiplink config=config %}
        {% skiplink option1='foo' option2='bar' %}

    Available options:

        - class: Optional, a string with additional CSS classes.
        - label_placeholder: Optional, alternative label to show as label.
        - target: Optional, The id of of the skiplink_target, defaults to 'skiplink-target'.


    :param kwargs:
    """
    kwargs = merge_config(kwargs)

    # i18n
    kwargs["label_to_content"] = parse_kwarg(
        kwargs, "label_to_content", _("Direct naar de inhoud.")
    )

    # kwargs
    kwargs["target"] = "#" + kwargs.get("target", "skiplink-target")

    kwargs["config"] = kwargs
    return kwargs


@register.inclusion_tag("rijkshuisstijl/components/skiplink/skiplink-target.html")
def skiplink_target(**kwargs):
    """
    Renders a skiplink (jump to content) target for screen readers.
    Should be used with skiplink.

    Example:

        {% skiplink_target config=config %}
        {% skiplink_target option1='foo' option2='bar' %}

    Available options:

        - class: Optional, a string with additional CSS classes.
        - id: Optional, The id of of the skiplink_target, defaults to 'skiplink-target'.


    :param kwargs:
    """
    kwargs = merge_config(kwargs)

    # kwargs
    kwargs["id"] = kwargs.get("id", "skiplink-target")

    kwargs["config"] = kwargs
    return kwargs


@register.inclusion_tag("rijkshuisstijl/components/textbox/textbox.html")
def textbox(**kwargs):
    """
    Renders a textbox.

    Example:

        {% textbox config=config %}
        {% textbox option1='foo' option2='bar' %}

    Available options:

        - class: Optional, a string with additional CSS classes.
        - close: Optional, If true, adds a close button to the textbox.
        - id: Optional, a string specifying the id, defaults to a generated uuid4 string.
        - status: Optional, A status string from the Django messages framework, styling the textbox accordingly.
        - title: Optional, Title to show.
        - text: Optional, Text to show.
        - wysiwyg: Optional, Raw HTML to be shown, styled automatically.
        - urlize: Optional, if True text is passed to "urlize" template filter, automatically creating hyperlinks.
        - urlize_target: Optional, "target" attribute for links generated using "urlize".

    :param config:
    """
    config = merge_config(kwargs)

    def get_wysiwyg():
        wysiwyg = config.get("wysiwyg")
        if wysiwyg:
            return mark_safe(wysiwyg)

    # kwargs
    config["class"] = config.get("class", None)
    config["close"] = parse_kwarg(config, "close", False)
    config["id"] = get_id(config, "textbox")
    config["status"] = config.get("status", None)
    config["title"] = config.get("title", None)
    config["text"] = config.get("text", None)
    config["wysiwyg"] = get_wysiwyg()
    config["urlize"] = config.get("urlize", True)
    config["urlize_target"] = config.get("urlize_target")

    config["config"] = config
    return config


class ParentNode(template.Node):
    """
    A Node which can contain nested children.
    All "TextNode" children will be skipped.
    Children are rendered and added to context["children"] as list.
    """

    def __init__(self, token, children, template_name):
        """
        Initializes this Node.
        :param token: The token providing the configuration for the parent.
        :param children: NodeList containing the children.
        :param template_name: The template name to use as template for the parent.
        """
        self.token = token
        self.children = children
        self.template_name = template_name

    def render(self, context):
        """
        Renders the parent.
        :param context:
        :return: SafeText
        """
        context_data = self.get_context_data(context)
        return render_to_string(self.template_name, context_data)

    def get_context_data(self, context):
        """
        Returns the context for the template of the parent.
        :param context:
        :return: dict
        """
        context_data = context.flatten()
        context_data["children"] = self.render_children(context)

        return {**self.get_config(), **context_data}

    def get_config(self):
        """
        Returns the parent config.
        :return: dict
        """
        split = self.token.split_contents()
        split.pop(0)
        config = {}

        for option in split:
            try:
                key, value = option.split("=")

                # Strip redundant quotes.
                if value[0] == '"' and value[-1] == '"':
                    value = value[1:-1]

                config[key] = parse_arg(value)
            except ValueError:
                pass
        return config

    def render_children(self, context):
        """
        Returns relevant children as str.
        :param context:
        :return: SafeText
        """
        children = self.get_children()

        rendered_children = []
        for child in children:
            rendered_child = self.render_child(child, context)
            if rendered_child.strip():
                rendered_children.append(rendered_child)
        return rendered_children

    def render_child(self, child, context):
        """
        Returns child as str
        :param child:
        :param context:
        :return: SafeText
        """
        return format_html(child.render(context))

    def get_children(self):
        """
        Returns relevant chilren (strips out "TextNode" instance).
        :return:
        """
        return [child for child in self.children if not isinstance(child, TextNode)]
