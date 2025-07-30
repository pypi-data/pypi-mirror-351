from django.forms import modelformset_factory
from django.utils.translation import gettext_lazy as _

from rijkshuisstijl.conf import settings
from rijkshuisstijl.templatetags.rijkshuisstijl import register
from rijkshuisstijl.templatetags.rijkshuisstijl_filters import getattr_or_get
from rijkshuisstijl.templatetags.rijkshuisstijl_helpers import (
    get_config_from_prefix,
    get_id,
    get_model,
    get_queryset,
    merge_config,
    parse_arg,
    parse_kwarg,
)
from rijkshuisstijl.templatetags.rijkshuisstijl_utils import (
    format_value,
    get_field_label,
)

try:
    from django.urls import reverse_lazy
except ImportError:
    from django.core.urlresolvers import reverse_lazy


@register.inclusion_tag("rijkshuisstijl/components/filter/filter.html")
def dom_filter(**kwargs):
    """
    Renders a realtime text filter for element in the DOM.
    Elements matching the given value are shown, others are hidden.
    All items are shown by default.

    Example:

        {% dom_filter config=config %}
        {% dom_filter option1='foo' option2='bar' %}

    Available options:

        - filter_target: Required, a queryselector string matching items which should be filtered.

        - class: Optional, a string with additional CSS classes.
        - input_class: Optional, a string with additional CSS classes for the input.
        - label_placeholder: Optional, alternative label to show as placeholder.
        - name: Optional, The name of the input.
        - value Optional, The (default) value of the input.

    :param kwargs:
    """
    kwargs = merge_config(kwargs)

    # i18n
    kwargs["label_placeholder"] = parse_kwarg(kwargs, "label_placeholder", _("Filteren op pagina"))

    # kwargs
    kwargs["class"] = kwargs.get("class", None)
    kwargs["input_class"] = ("filter__input " + kwargs.get("input_class", None)).strip()
    kwargs["filter_target"] = kwargs.get("filter_target", "")
    kwargs["name"] = kwargs.get("name", None)
    kwargs["value"] = kwargs.get("value", None)

    kwargs["config"] = kwargs
    return kwargs


@register.inclusion_tag("rijkshuisstijl/components/icon/icon.html")
def icon(icon=None, **kwargs):
    """
    Renders an icon.

    Example:

        {% icon 'foo' %}
        {% icon config=config %}
        {% icon option1='foo' option2='bar' %}

    Available options:

        - icon: Optional, The name of the icon to be rendered, can be defined by first argument.
        - src: Optional, The source of the icon to be rendered.

        - class: Optional, a string with additional CSS classes.
        - href: Optional, an optional url to link to.
        - label: Optional, An additional label to show.

    :param icon:
    :param kwargs:
    """
    kwargs = merge_config(kwargs)

    # kwargs
    kwargs["class"] = kwargs.get("class", None)
    kwargs["href"] = kwargs.get("href", None)
    kwargs["icon"] = kwargs.get("icon", None)
    kwargs["label"] = kwargs.get("label", None)
    kwargs["src"] = kwargs.get("src", None)

    # args
    kwargs["icon"] = icon

    kwargs["config"] = kwargs
    return kwargs


@register.inclusion_tag("rijkshuisstijl/components/key-value-table/key-value-table.html")
def key_value_table(**kwargs):
    """
    Renders an key/value table.

    Example:

        {% key_value_table config=config %}
        {% key_value_table option1='foo' option2='bar' %}

    Available options:

    - fields: Required, A dict (key, label) or a list defining which attributes of object to show and what labels to
      use.

      - If a dict is passed, each key will represent a field in an object to obtain the data from and each value
        will represent the label to use for the column heading.
        Example: {'author': 'Written by', 'title': 'Title'}

      - If a list is passed, each item will represent a field in an object to obtain the data from and will also
        represent the label to use for the column heading.
        Example: ['author', 'title']

        - Within a list, a dict may be passed.
          Example: ['author': {'key': 'author', 'label': 'Written by'}, 'title']

      - A label can be a callable in which case it will receive the object as argument and the returned value is
        used as label.
        Example: ['author': {'key': 'author', 'label': lambda x: str(x) +' is written by'}, 'title']

    - object: Required, An object containing the keys defined fields.
    - field_toggle_edit: Optional, If true (and form is set) allows toggle between value and input for each value.
    - form: Optional, A (Django) form instance which fields become editable in the key/value table if provided.
    - form_action: Optional,
    - form_enctype: Optional,
    - form_method: Optional,
    - form_id: Optional, Optional, if set, value will be set on the "form" attribute of generated inputs. No <form>
      tag will be created. This makes the input part of the referenced form.
    - formset_valid: Optional, callback when formset saved successfully, called with arguments (request, instances)
    - full_width_fields: Optional, a list of keys of fields that should take the full width of the component.
    - class: Optional, a string with additional CSS classes.
    - urlize: Optional, if True (default) cell values are passed to "urlize" template filter, automatically creating
      hyperlinks if applicable in every cell.
    - urlize_target: Optional, "target" attribute for links generated using "urlize".

    Custom presentation (get_<field>_display)
    -----------------------------------------

    - get_<field>_display: Optional, allows a callable to be used to generate a custom display value. Replace <field>
    with a key which will map to a field  and set a callable as it's value.

    The callable will receive the row's object and should return SafeText.
    Example: `lambda object: mark_safe(<a href="{}">{}</a>.format(object.author.get_absolute_url, object.author))`

    :param kwargs:
    """
    return key_value("key-value-table", **kwargs)


@register.inclusion_tag("rijkshuisstijl/components/summary/summary-list.html", takes_context=True)
def summary_list(context, **kwargs):
    """
    Shows multiple "summary" components for every object in "object_list" option.
    Shares the interface with summary (see: key_value_table) with the exception of using object_list instead of object.


    Inline forms (formsets)
    -----------------------

    Values within te summary list can be changed using formsets. To enable these "inline forms" specify the form_class
    option and pass a (Django) ModelForm class specifying fields matching the columns.

    - form_class: Optional, a (Django) Form class specifying the fields to be editable.
    """
    config = merge_config(kwargs)

    def get_formset():
        """
        :return: BaseModelFormSet
        """
        request = context.get("request")
        form_class = config.get("form_class")
        formset_valid = config.get("formset_valid")
        model = get_model(context, config)
        queryset = get_queryset(context, config)

        if not (form_class and model):
            return

        ModelFormSet = modelformset_factory(model, form_class, extra=0)

        if request.method == "POST":
            formset = ModelFormSet(request.POST)

            if formset.is_valid():
                instances = formset.save()
                # Reset the cache for fresh data
                queryset = queryset.all()
                config["object_list"] = queryset
                if formset_valid:
                    formset_valid(request, instances)
                return ModelFormSet(queryset=queryset)
            else:
                return formset
        return ModelFormSet(queryset=queryset)

    config["id"] = get_id(config, "summary-list")
    config["object_list"] = parse_kwarg(config, "object_list", [])
    config["formset"] = get_formset()
    config["help_text_position"] = parse_kwarg(
        config, "help_text_position", settings.RH_HELP_TEXT_POSITION
    )
    config["show_toggle"] = parse_kwarg(config, "show_toggle", False)
    config["config"] = config
    return config


@register.inclusion_tag("rijkshuisstijl/components/summary/summary.html")
def summary(**kwargs):
    """
    An alternative representation of "key_value_table" with the same interface (see: key_value_table).
    In addition to key_value_table options: "detail_fields" can be specified (same syntax as "fields". Setting this will
    result in a collapsible section in the summary.

    Example:

        {% summary config=config %}
        {% summary option1='foo' option2='bar' %}

    (Additional) available options:

    - toolbar_*: Prefixed configuration, adds a toolbar. See toolbar.

    """

    def get_href(object, href):
        if callable(href):
            return href(object)
        return config

    config = key_value("summary", **kwargs)
    object = config.get("object")
    config["toolbar_items"] = [{**item, "href": get_href(object, item.get("href"))} for item in config.get("toolbar_items", [])]
    config["toolbar_config"] = get_config_from_prefix(config, "toolbar")
    return config


def key_value(component, **kwargs):
    """
    Shared between key_value table and summary.
    """
    config = merge_config(kwargs)
    _cache = {}

    def get_data(fields_key):
        """
        Return a list of tuples for every fieldset, creates a default fieldset is none provided.
        Every fieldset tuple contains a title and a list of dict (label, value) for every field in object.
        :param fields_key: A str containing the key to obtain fields from.
        :return:
        """

        # Normalize config["fields"] to tuple.
        fields = parse_kwarg(config, fields_key, [])
        fields_list = get_fields(fields)
        field_keys = [f.get("key") for f in fields_list]

        # Get fieldsets or default fieldset.
        fieldsets = parse_kwarg(config, "fieldsets", [(None, {"fields": field_keys})])

        # Always build fieldset structure (with at least one fieldset).
        data = []
        for fieldset in fieldsets:
            fieldset_title = fieldset[0]
            fieldset_keys = fieldset[1].get("fields", ())

            if component == "summary":
                fieldset_field_keys = [fk for fk in fieldset_keys if fk in field_keys]
            else:
                fieldset_field_keys = [fk for fk in fieldset_keys]

            # Only show populated fieldsets.
            if len(fieldset_field_keys):
                field_dict = [f for f in fields_list if f.get("key") in fieldset_field_keys]
                data.append((fieldset_title, field_dict))

        return data

    def get_fields(fields):
        """
        Converts fields to a dict with additional context for each field.
        :param fields: A dict (key, label) or a list defining which attributes of object to show and what labels to use.
        :return: A list_of_dict (id, edit, form_field, toggle, full_width_field, key, label, value) for every field in in fields.
        """
        form = config.get("formset_form", config.get("form"))
        key_value_id = get_key_value_id()
        obj = config.get("object")

        fields = [
            {
                "id": f"{key_value_id}-{get_key_value_key(field)}",
                "full_width_field": get_key_value_key(field) in get_full_width_fields(),
                "key": get_key_value_key(field),
                "label": get_field_label(obj, get_key_value_label(fields, field)),
                "value": format_value(obj, get_key_value_key(field)),
            }
            for field in fields
        ]

        if form:
            for field in fields:
                key = get_key_value_key(field)

                if key in form.fields:
                    field["form_field"] = form[key]
                    field["edit"] = not get_field_toggle_edit() or key in form.errors
                    field["toggle"] = get_field_toggle_edit()

        return fields

    def get_key_value_id():
        if _cache.get("get_key_value_id"):
            return _cache.get("get_key_value_id")

        id = get_id(config, component)

        _cache["get_key_value_id"] = id
        return id

    def get_full_width_fields():
        if _cache.get("get_full_width_fields"):
            return _cache.get("get_full_width_fields")

        full_width_fields = parse_kwarg(config, "full_width_fields", [])

        _cache["get_full_width_fields"] = full_width_fields
        return full_width_fields

    def get_key_value_key(field):
        return get_field_item_by_key(field, "key")

    def get_key_value_label(fields, field):
        try:
            return fields.get(field)
        except AttributeError:
            return get_field_item_by_key(field, "label")

    def get_field_item_by_key(field, key):
        try:
            return field[key]
        except (AttributeError, TypeError):
            return field

    def get_field_toggle_edit():
        if _cache.get("get_field_toggle_edit"):
            return _cache.get("get_field_toggle_edit")

        field_toggle_edit = parse_kwarg(config, "field_toggle_edit", False)

        _cache["get_field_toggle_edit"] = field_toggle_edit
        return field_toggle_edit

    def add_object_attributes(config):
        """
        Calls add_display(obj) and add_modifier_class(obj) for every obj in (paginated) object_list.
        :param config:
        :return: datagrid_context
        """
        obj = config.get("object", None)
        if obj:
            add_display(obj, config)
        return config

    def add_display(obj, config):
        """
        If a get_<field>_display callable is set, add the evaluated result to the rh_display_<field> field on the
        object passed to obj.
        :param obj:
        """
        fields = config.get("fields", {})
        for field in fields:
            fn = config.get("get_{}_display".format(field), None)
            if fn:
                setattr(obj, "rh_display_{}".format(field), fn(obj))

    # config
    config["class"] = config.get("class", None)
    config["id"] = get_key_value_id()
    config["data"] = get_data("fields")
    config["detail_data"] = get_data("detail_fields")
    config["field_toggle_edit"] = get_field_toggle_edit()
    config["form"] = config.get("form", None)
    config["form_action"] = config.get("form_action", None)
    config["form_method"] = config.get("form_method", "post")
    config["form_enctype"] = config.get("form_enctype", "multipart/form-data")
    config["full_width_fields"] = get_full_width_fields()
    config["object"] = config.get("object", None)
    config["help_text_position"] = config.get("help_text_position", settings.RH_HELP_TEXT_POSITION)
    config["urlize"] = parse_kwarg(config, "urlize", True)
    config["urlize_target"] = parse_kwarg(config, "urlize_target")
    config = add_object_attributes(config)

    config["config"] = config
    return config


@register.inclusion_tag("rijkshuisstijl/components/paginator/paginator.html", takes_context=True)
def paginator(context, **kwargs):
    """
    Renders a paginator.

    Example:

        {% paginator config=config %}
        {% paginator option1='foo' option2='bar' %}

    Available options:

        - paginator: Required, A Django Paginator instance, may be obtained from context.
        - page_obj: Required, The paginator page object, may be obtained from context.

        - class: Optional, a string with additional CSS classes.
        - form: Optional, if True (default), sets the paginator tag to "form" uses "div" if set to False. A str can be
          passed to set the value of the "form" attribute on the input in which case the paginator tag is set to "div",
          this allows linking the input to a custom form.
        - is_paginated: Optional, if true (default), render the paginator.
        - label_page: Optional, alternative label to show for "Pagina".
        - label_from: Optional, alternative label to show for "van".
        - label_first: Optional, alternative label to show for first page.
        - label_previous: Optional, alternative label to show for previous page.
        - label_next: Optional, alternative label to show for next page.
        - label_last: Optional, alternative label to show for last page.

        - page_number: Optional, The current page number.
        - page_key: Optional, The GET parameter to use for the page, defaults to 'page'.

    :param context:
    :param kwargs:
    """
    config = merge_config(kwargs)

    def get_form():
        return parse_kwarg(kwargs, "form", True)

    def get_form_id():
        """
        Returns "form" as form_id if it's not parsed to a bool.
        This allows a custom form to be linked using the "form" attribute on the input.
        :return: str or None
        """
        form = get_form()
        if not type(form) is bool:
            return form
        return None

    def get_is_paginated():
        return kwargs.get("is_paginated", context.get("is_paginated"))

    def get_paginator():
        return kwargs.get("paginator", context.get("paginator"))

    def get_page_min():
        return 1

    def get_page_max():
        paginator = get_paginator()
        return paginator.num_pages

    def get_page_number():
        page_obj = get_page_obj()

        if page_obj:
            return page_obj.number

        return kwargs.get("page_number", 1)

    def get_page_key():
        return kwargs.get("page_key", "page")

    def get_page_obj():
        return kwargs.get("page_obj", context.get("page_obj"))

    def get_tag():
        """
        Returns the tag to use for the paginator (defaults to "form"). Returns "div" is either form is set to False or a
        str with a custom form id.
        """
        form = get_form()

        if form is True:
            return "form"
        return "div"

    # i18n
    config["label_page"] = parse_kwarg(kwargs, "label_page", _("Pagina"))
    config["label_from"] = parse_kwarg(kwargs, "label_from", _("van"))
    config["label_previous"] = parse_kwarg(kwargs, "label_previous", _("Vorige"))
    config["label_next"] = parse_kwarg(kwargs, "label_next", _("Volgende"))
    config["label_last"] = parse_kwarg(kwargs, "label_last", _("Laatste"))

    # kwargs
    config["class"] = kwargs.get("class", None)
    config["form"] = get_form()
    config["form_id"] = get_form_id()
    config["is_paginated"] = get_is_paginated()
    config["paginator"] = get_paginator()
    config["page_min"] = get_page_min()
    config["page_max"] = get_page_max()
    config["page_number"] = get_page_number()
    config["page_key"] = get_page_key()
    config["page_obj"] = get_page_obj()
    config["tag"] = get_tag()

    config["request"] = context["request"]
    config["config"] = kwargs
    return config


@register.inclusion_tag("rijkshuisstijl/components/stacked-list/stacked-list.html")
def stacked_list(*args, **kwargs):
    """
    Renders a stacked list, optionally containing hyperlinks.

    Example:

        {% stacked_list 'foo' 'bar' %}
        {% stacked_list config=config %}
        {% stacked_list option1='foo' option2='bar' %}

    Available options:

        - class: Optional, a string with additional CSS classes.
        - field: Optional, a key in every object in object_list.
        - items: Optional, a dict (label, [url]) or a list defining with values to show, can be obtained from args.
        - url_field: Optional, A key in every object on object_list for a URL, creates hyperlinks.
        - url_reverse: Optional, A URL name to reverse using the object's 'pk' attribute as one and only attribute,
          creates hyperlinks.
        - object_list: Optional, a list of objects for which to show the value of the attribute defined by field.

    :param args:
    :param kwargs:
    """
    kwargs = merge_config(kwargs)

    def get_items():
        object_list = kwargs.get("object_list")
        field = kwargs.get("field")
        items = []

        if object_list and field:
            items = [get_item(obj, field) for obj in object_list]

        return items + kwargs.get("items", [])

    def get_item(obj, field):
        url_field = kwargs.get("url_field")
        url_reverse = kwargs.get("url_reverse")
        item = {"label": getattr_or_get(obj, field)}

        if url_field:
            item["url"] = getattr_or_get(obj, url_field)

        if url_reverse:
            item["url"] = reverse_lazy(url_reverse, object.pk)

        if "url" in item and not item["url"]:
            try:
                if item.get_absolute_url:
                    item["url"] = item.get_absolute_url
            except AttributeError:
                pass

        return item

    # kwargs
    kwargs["class"] = kwargs.get("class", None)
    kwargs["items"] = get_items()

    # args
    for arg in args:
        arg_items = arg
        if not hasattr(arg, "__iter__"):
            arg_items = [arg]

        for item in arg_items:
            kwargs["items"].append(parse_arg(item))

    kwargs["config"] = kwargs
    return kwargs


@register.inclusion_tag("rijkshuisstijl/components/title-header/title-header.html")
def title_header(title=None, **kwargs):
    """
    Renders a title.

    Example:

        {% title_header config=config %}
        {% title_header option1='foo' option2='bar' %}

    Available options:

        - title: Required, The title to show, may be obtained from first argument.

        - class: Optional, a string with additional CSS classes.

    :param title:
    :param kwargs:
    """
    config = merge_config(kwargs)

    # kwargs
    config["class"] = config.get("class")
    config["title"] = config.get("title", title)
    config["body"] = config.get("body")

    config["config"] = config
    return config


@register.inclusion_tag("rijkshuisstijl/components/toolbar/toolbar.html")
def toolbar(*args, **kwargs):
    """
    Renders a toolbar populated with buttons, (see rijkshuisstijl_form.button).

    Example:

        {% toolbar config=config %}
        {% toolbar option1='foo' option2='bar' %}

    Available options:

        - class: Optional, a string with additional CSS classes.
        - items: Optional, a list_of_dict (label, [href], [icon], [name], [target], [title]) defining which buttons to
          create (see rijkshuisstijl_form.button).

    :param args:
    :param kwargs:
    """
    kwargs = merge_config(kwargs)

    # kwargs
    kwargs["class"] = kwargs.get("class", None)
    kwargs["items"] = kwargs.get("items", [])

    # args
    for arg in args:
        arg_items = arg
        if not hasattr(arg, "__iter__"):
            arg_items = [arg]

        for item in arg_items:
            kwargs["items"].append(parse_arg(item))

    for item in kwargs["items"]:
        item["class"] = item.get("class", "button--hover button--icon-left")
        item["config"] = item

    kwargs["config"] = kwargs
    return kwargs
