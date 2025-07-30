import re
from datetime import timedelta

from django.core.exceptions import FieldDoesNotExist, FieldError
from django.core.paginator import Paginator
from django.forms import modelformset_factory
from django.http import QueryDict
from django.utils.dateparse import parse_date, parse_datetime
from django.utils.timezone import make_aware
from django.utils.translation import gettext_lazy as _

from rijkshuisstijl.templatetags.rijkshuisstijl import register
from rijkshuisstijl.templatetags.rijkshuisstijl_filters import getattr_or_get
from rijkshuisstijl.templatetags.rijkshuisstijl_utils import (
    get_recursed_field_label,
    get_recursed_field_value,
)

from .rijkshuisstijl_helpers import (
    create_list_of_dict,
    get_id,
    get_model,
    get_model_label,
    get_object_list,
    get_queryset,
    merge_config,
    parse_kwarg,
)


@register.inclusion_tag("rijkshuisstijl/components/datagrid/datagrid.html", takes_context=True)
def datagrid(context, **kwargs):
    """
    Renders a table like component with support for filtering, ordering and  paginating. It's main use if to display
    data from a listview.

    .. code-block:: html

        {% datagrid config=config %}
        {% datagrid option1='foo' option2='bar' %}

    Available options
    =================

    Showing data
    ------------

    Data is shown based on a internal "object" list which can be populated by either a "queryset" or an
    "object_list option. Columns are specified by a "columns" option which may define an additional label to show in
    the table header. Columns match fields in the objects in the internal object_list.

    - object_list: Optional, A list containing the object_list to show. if possible, use queryset instead.
      The internally used object_list is obtained by looking for these values in order:

    .. code-block:: python

        config['queryset']
        config['object_list']
        context['queryset']
        context['object_list']

    - queryset: Optional, A queryset containing the objects to show.

    - columns: Required, a dict ("key", "label"), a list_of_dict ("key", "lookup", "label", "filter_label", "width",
      "urlize") or a list defining which columns/values to show for each object in object_list or queryset.

      - If a dict is passed, each key will represent a field in an object to obtain the data from and each value
        will represent the label to use for the column heading.
        Example: {'author': 'Written by', 'title': 'Title'}

      - If a list_of_dict is passed:
          - "key" will represent a field in an object to obtain the data from.
          - "lookup" key can be passed to point to a different field/method providing a value. In this case "key" will
             still be used when a (Model) field is referenced (if QuerySet is passed or obtained from context).
          - "export_lookup" key can be passed to point to a different field/method providing a value when exporting.
             Note: this will only affect the value of export_input_name, actual export relies on custom implementation.
          - "label" key can be supplied to set the column heading. if not set and a QuerySet is passed, an attempt will
             be made to resolve the verbose_name from the model as column heading.
          - "filter_label" key can be passed to set a custom placeholder label on the filter.
          - "width" can be set to a CSS value valid for width.
        Example: [{"key": "author", "lookup": "author__first_name", "label": "Written by", "width: "10%"}]

      - If a list is passed, each item will represent a field in an object to obtain the data from and will also
        represent the label to use for the column heading or, if a QuerySet is passed or obtained from the context, an
        attempt will be made to resolve the verbose_name from the model as column heading.
        Example: ['author', 'title']


    Filtering
    ---------

    If an (unpaginated) QuerySet is passed or obtained from the context, it can be filtered using controls.
    Pagination provided by the datagrid itself can be used in combination with filtering. The queryset's model is
    inspected to determine the type of the filters and optionally the choices.

    - filterable_columns: Optional, a dict ("key", "label"), a list_of_dict ("key", "lookup", "label", "filter_label",
      "width") or a list defining which columns should be filterable. This may be configured equally to "columns".

    - filter_action: Optional, specifies the url to submit filter actions to, this can be omitted in most cases.

    - filter_query_params: Optional, a list_of_dict ("key", "value") specifying additional query parameters for
      filtering.


    DOM filter
    ----------

    Next to queryset filters, a DOM filter can be added to the top header allowing real time searching within the page.
    See: rijkshuisstijl.templatetags.rijkshuisstijl_extras.dom_filter.

    - dom_filter: Optional, if True, adds a DOM filter to the top header.


    Grouping
    --------

    Objects can be grouped together within the datagrid by specifying the "groups" options. This resolves the value of
    "lookup" for each shown object and tests it against each "value" in a dict in "groups", a subtitle for each group is
    rendered showing the value of "label" within that same dict.

    - groups: Optional, a dict ("lookup", "values"). Lookup should be a string pointing to a (related) field. Groups
      should be a list_of_dict ("value", "label"). The result the lookup for each object is compared to the value of
      each group. Optionally, a callable can be passed to lookup in which case it will be called with obj as first
      argument and the returned value will be used as value to test against.


    Ordering
    --------

    An interface for ordering can be creating by defining the fields that should be made orderable. Orderable
    columns are specified by the "orderable_columns" option which may define a field lookup which defaults to the
    field. Inverted field lookups are proceeded with a dash "-" character and set to the GET parameter specified by
    the "ordering_key" setting.

    - order: Optional, if True, order queryset, if False rely on view/context to order queryset.
    - orderable_columns: Optional, a dict or a list defining which columns should be orderable.

      - If a dict is passed each key will map to a field (the key) in columns, each value will be used to describe
        a field lookup.
        Example: {"author": "author__first_name"}

      - If a list is passed each value will map to a field (the key) in columns and will also be used to describe
        a field lookup.
        Example: ['author', 'title']

      - Additionally, a dict ("key", ["lookup"]) can be passed within a list.
        a field lookup.
        Example: ['{"key": "author", "lookup": "author__first_name"}', 'title']

    - ordering_key: Optional, describes which query parameter should be used in hyperlinks
    (set on the table captions) to indicate which order the view should provide, defaults to "ordering".


    Pagination
    ----------

    Data can be paginated if needed. Pagination can either be performed by the datagrid itself, or an already
    available (Django) paginator may be used (since we need to support already paginated object lists).

    Paginate un-paginated object_list
    ---------------------------------

    - paginate: Optional, if True, paginate object_list (or queryset).
    - paginate_by: Optional, amount of results per page, defaults to 100.
    - page_key: Optional, The GET parameter to use for the page, defaults to 'page'.

    Use existing paginator
    ----------------------

    An existing Django Paginator instance can be used. Pagination details may be obtained from the context if not
    explicitly set.

    - is_paginated: Optional, if True, paginate based on paginator configuration, may be obtained from context.
    - paginator: Optional, A Django Paginator instance, may be obtained from context.
    - page_obj: Optional, The paginator page object, may be obtained from context.
    - page_number: Optional, The current page number.
    - page_key: Optional, The GET parameter to use for the page, defaults to 'page'.


    Custom presentation (get_<field>_display)
    -----------------------------------------

    - get_<field>_display: Optional, allows a callable to be used to generate a custom cell display value. Replace
      <field> with a key which will map to a field (a key in columns) and set a callable as it's value.

    The callable will receive the row's object and should return SafeText.
    Example: `lambda object: mark_safe(<a href="{}">{}</a>.format(object.author.get_absolute_url, object.author))`


    Manipulating data (form)
    ------------------------

    A form can be generated POSTing data to the url specified by the "form_action" option. When a form is active
    each row gets a checkbox input with a name specified by the "form_checkbox_name" option. Various actions can be
    defined by the "form_buttons" option which are placed either in the top, bottom or at both position based on the
    value of the "toolbar_position" option. For creating inline forms, see "inline forms (formsets)".

    - form: Optional, if True, adds a form to the datagrid, useful for allowing user manipulations on the dataset.
      Defaults to false, unless "form_action" or "form_buttons" is set.

    - form_action: Optional, specifies the url to submit form actions to. If set, form will default to True.

    - form_method: Optional, method to use for the form, defaults to "POST".

    - form_buttons: Optional, a list_of_dict (label, [href], [icon], [icon_src] [name], [target], [title]) defining
      which buttons to create (see rijkshuisstijl_form.button). The name attribute of the buttons should be used to
      specify the performed action.
      example: [{'name': 'delete', 'label': 'delete' 'class': 'button--danger'}]

    - form_checkbox_name: Optional, specifies the name for each checkbox input for an object in the table. This
      should be used for determining which objects should be manipulated by the performed action.

    - form_select_all_position, Specifies the position of the select all checkbox (if applicable).

    - form_select: Optional, If set (dict, at least "name"), shows a select with actions (comparable to form_buttons).
      Requires form_options to be set as well. The name attribute should be used to specify the performed action.

    - form_options: Optional, a list_of_dict (label, value) defining which options to create within the select.

    - form_model_name: Optional, A str indicating the name of the input used to pass the model to export.
      Note: actual export relies on custom implementation.

    - formset_valid: Optional, callback when formset saved successfully, called with arguments (request, instances)

    - export_buttons: Optional, similar to "form_buttons" except rendered differently, these buttons indicate possible
      export formats. Note: actual export relies on custom implementation.

    - export_input_name: Optional, A str indicating the name of the input used to pass the columns to export.
      Note: actual export relies on custom implementation.

    - toolbar_position: Optional, a list_of_dict (value, label) defining
      toolbar containing the buttons specified by form_buttons.


    Inline forms (formsets)
    -----------------------

    Values within te datagrid can be changed using formsets. To enable these "inline forms" specify the form_class
    option and pass a (Django) form class specifying fields matching the columns.

    - form_class: Optional, a (Django) ModelForm class specifying the fields to be editable.

    Color coded rows
    ----------------

    Rows can be configured to show a color coded border and a colored cell value based on the value of a certain
    field. The field to look for is defined by the "modifier_key" option if this is any different than the column
    key it should color the cell for, the column can be specified by the "modifier_column" options. This defaults
    to the value of the "modifier_key" option. The field value is matched against a mapping (specified by the
    "modifier_mapping" options) to define the color. The value should contain the value in the mapping.

    - modifier_key Optional, a string defining the field in an object to get the value to match for.
    - modifier_column Optional, a string defining the column key to apply the colored styling for.
    - modifier_mapping, Optional, a dict containing a key which possibly partially matches an object's field value
      and which value is one of the supported colors.
      Example: [{'1984': 'purple'}]

    The supported colors are:

    purple, purple-shade-1, purple-shade-2, violet, violet-shade-1, violet-shade-2, ruby, ruby-shade-1, ruby-shade-2,
    pink, pink-shade-1, pink-shade-2, red, red-shade-1, red-shade-2, orange, orange-shade-1, orange-shade-2,
    dark-yellow, dark-yellow-shade-1, dark-yellow-shade-2, yellow, yellow-shade-1, yellow-shade-2, dark-brown,
    dark-brown-shade-1, dark-brown-shade-2, brown, brown-shade-1, brown-shade-2, dark-green, dark-green-shade-1,
    dark-green-shade-2, green, green-shade-1, green-shade-2, moss-green, moss-green-shade-1, moss-green-shade-2,
    mint-green, mint-green-shade-1, mint-green-shade-2, dark-blue, dark-blue-shade-1, dark-blue-shade-2, heaven-blue,
    heaven-blue-shade-1, heaven-blue-shade-2, light-blue, light-blue-shade-1, light-blue-shade-2


    Additional options
    ------------------

    - class: Optional, a string with additional CSS classes.
    - id: Optional, a string specifying the id, defaults to a generated uuid4 string.
    - title: Optional, if set, a title will be shown above the datagrid.
    - url_reverse: Optional, A URL name to reverse using the object's 'pk' attribute as one and only attribute,
      creates hyperlinks in the first cell. If no url_reverse if passed get_absolute_url is tried in order to find
      a url.
    - urlize: Optional, if True (default) cell values are passed to "urlize" template filter, automatically creating. Passing FQN urls to this filter will cause urlize to be ran twice which lead to unwanted behaviour, set urlize to False on a column basis to prevent this.
      hyperlinks if applicable in every cell.

    :param context:
    :param kwargs:
    """

    # Keep a quick cache single use _cache dict to speed things up a bit, we might need to optimize this later.
    _cache = {}

    def get_datagrid_id(config):
        if _cache.get("get_datagrid_id"):
            return _cache.get("get_datagrid_id")

        datagrid_id = get_id(config, "datagrid")

        _cache["get_datagrid_id"] = datagrid_id
        return datagrid_id

    def get_columns():
        """
        Gets the columns to show based on config['columns']. If no label is provided an attempt is made to create it
        based on the model or a simple replacement of dashes and underscores.
        :return: A list_of_dict where each dict contains "key" and "label" keys.
        """
        if _cache.get("get_columns"):
            return _cache.get("get_columns")

        columns = parse_kwarg(config, "columns", [])
        columns = create_list_of_dict(columns, "key", "fallback_label")
        queryset = get_queryset(context, config)

        # Get column label.
        model = get_model(context, config)

        for column in columns:
            # Default lookup.
            column["lookup"] = column.get("lookup", column.get("key"))
            column["export_lookup"] = column.get("export_lookup", column.get("lookup"))

            # If queryset present, resolve label via model.
            if model and not column.get("label"):
                column["label"] = get_recursed_field_label(model, column["key"])

            # If queryset not present, fall back to fallback label.
            if not queryset and not column.get("label"):
                column["label"] = column.get("fallback_label")

        _cache["get_columns"] = columns
        return columns

    def get_datagrid_object_list(refresh=False):
        """
        Looks for the object_list to use based on the presence of these variables in order:

            1) config['queryset']
            2) config['object_list']
            3) context['queryset']
            4) context['object_list']

        Queryset filtering is applied if required.
        Ordering is applied if required.
        add_display() and add_modifier_class() are called for every object in the found object_list.
        :return: A list of objects to show data for.
        """
        if _cache.get("get_object_list") and not refresh:
            return _cache.get("get_object_list")

        # Get object list.
        object_list = get_object_list(context, config)

        if get_model(context, config) and refresh:
            object_list = object_list.all()

        # Filtering.
        object_list = get_filtered_queryset(object_list)

        # Ordering.
        order = config.get("order")
        if order and hasattr(object_list, "order_by") and callable(object_list.order_by):
            order_by = get_ordering()

            if order_by:
                object_list = object_list.order_by(order_by)

        # Pagination
        object_list = add_paginator(object_list)

        _cache["get_object_list"] = object_list
        return object_list

    def get_filtered_queryset(object_list):
        """
        Fitlers the QuerySet (if set) based on provided filter input.
        :return: List or QuerySet
        """
        if _cache.get("get_filtered_queryset"):
            return _cache.get("get_filtered_queryset")

        filters = get_filters()
        model = get_model(context, config)

        if filters and model:
            # Active filters (with value set).
            active_filters = [
                active_filter for active_filter in filters if active_filter.get("value")
            ]

            # Filter one filter at a time.
            for active_filter in active_filters:
                lookup = active_filter.get("lookup")
                filter_value = active_filter.get("value")
                filter_type = active_filter.get("type")

                # Bypass filter if set.
                if active_filter.get("bypass_filter", False):
                    continue

                # "filter_queryset".
                elif active_filter.get("filter_queryset") or active_filter.get('choices'):
                    filter_kwargs = {lookup: filter_value}

                # Date.
                elif filter_type in ["DateField", "DateTimeField"]:  # TODO: DateTimeField
                    dates = re.split(r"[^\d-]+", filter_value)

                    if len(dates) == 1:
                        date_end = parse_date(dates[0]) + timedelta(days=1)
                        date_end_string = date_end.isoformat()
                        dates.append(date_end_string)

                    try:
                        dates = [make_aware(parse_datetime(d)) for d in dates]
                    except AttributeError:
                        dates = [make_aware(parse_datetime(d + " 00:00:00")) for d in dates]

                    filter_kwargs = {f"{lookup}__range": dates}

                # Related field.
                elif active_filter.get("is_relation"):
                    filter_kwargs = {lookup: filter_value}

                # Anything else.
                else:
                    filter_kwargs = {lookup + "__icontains": filter_value}

                # Run filter using ORM.
                try:
                    object_list = object_list.filter(**filter_kwargs)

                # We can't filter on this using ORM, filter using Python instead (slow).
                except FieldError as e:
                    # Build a list of primary keys of objects matching our filter.
                    pks = []
                    for obj in object_list:
                        obj_value = get_recursed_field_value(obj, lookup)

                        # If we have a function, call it, use it's return value in comparison.
                        if callable(obj_value):
                            obj_value = obj_value()

                        if filter_value.upper() in str(obj_value).upper():
                            pks.append(obj.pk)

                    # Run filter.
                    object_list = object_list.filter(pk__in=pks)

        _cache["get_filtered_queryset"] = object_list
        return object_list

    def get_modifier_column():
        """
        Returns the key of the column to colorize the value of is a modifier configuration is set. Defaults to the value
        of the modifier_key option.
        :return: A string othe modifier column or False.
        """
        return config.get("modifier_column", config.get("modifier_key", False))

    def get_filters():
        """
        Returns a list_of_dict for filter configuration, each dict (if present) contains:

        - lookup: matching a column.
        - type: matching the field class name.
        - choices: a tuple containing choice tuples. Used to provide options/suggestions for filter.
        - value: The value of the filter.

        :return: list_of_dict.
        """
        if _cache.get("get_filters"):
            return _cache.get("get_filters")

        # Get the columns configured to be filterable.
        filterable_columns = parse_kwarg(config, "filterable_columns", [])
        filterable_columns = create_list_of_dict(filterable_columns)

        # Get the model.
        model = get_model(context, config)

        # Filtering is only supported on QuerySets.
        if not model:
            _cache["get_filters"] = {}
            return {}

        # Create configuration dict for each filterable_column.
        for filterable_column in filterable_columns:

            #
            # Set the column key and the "lookup", this determines the actual value to filter against.
            # This QuerySet is filtered in get_filtered_queryset()
            #

            # Use either the "key" as filter field, of optionally, the "lookup".
            filter_field_key = filterable_column.get("key", "")
            filter_field_lookup = filterable_column.get(
                "filter_lookup", filterable_column.get("lookup", "")
            )

            try:
                column = [column for column in get_columns() if column['key'] == filter_field_key][0]
            except:
                column = {}

            # Set label.
            filter_field_filter_label = filterable_column.get("filter_label")
            column_filter_label = column.get("filter_label")
            column_label = column.get("label")
            filter_field_label = filterable_column.get("label")
            filterable_column[
                "filter_label"] = filter_field_filter_label or column_filter_label or filter_field_label or column_label

            # Default the lookup to filter_field_key.
            # This is used in get_filtered_queryset().
            if not "lookup" in filterable_column:
                filterable_column["lookup"] = filter_field_lookup or filter_field_key

            #
            # Find out what model and field the filter should work with.
            # This can be the model of the QuerySet or a related model.
            #

            # Create a split for lookup, start with the first item as filter_field_name.
            fields_split = filter_field_key.split("__")
            filter_field_name = fields_split[0]

            # The default filter_model and filter_field.
            filter_model = model
            try:
                filter_field = filter_model._meta.get_field(filter_field_name)
            except FieldDoesNotExist:
                filter_field = False

            # If we're dealing with related items, search for the related filter_model and filter_field in fields_split.
            while fields_split:
                field = fields_split.pop(0)

                try:
                    remote_field = filter_model._meta.get_field(field).remote_field

                    # Not a remote field, break.
                    if remote_field is None:
                        break

                    filter_field = remote_field
                    filter_model = filter_field.model

                except (AttributeError, FieldDoesNotExist):
                    break

            #
            # We now know the (related) model and field for the filter.
            # Set the type and choices based on this.
            #

            # If no type has been set, find it based on the field.
            if not "type" in filterable_column:
                filterable_column["type"] = type(filter_field).__name__

            # If not choices have been set, find them based on the field.
            if not "choices" in filterable_column or "is_relation" in filterable_column:
                try:
                    # Default choices.
                    choices = getattr(filter_field, "choices", [])

                    # Allow a "filter_queryset" to be set.
                    if "filter_queryset" in filterable_column:
                        choices = filterable_column.get("filter_queryset")

                    # A boolean field gets choices for the boolean values.
                    elif filterable_column.get("type") == "BooleanField":
                        choices = ((True, _("waar")), (False, _("onwaar")))

                    # A related field gets choices for all related objects. This can be slow if a lot of objects are found.
                    # To avoid this, set "choices" in dict in filterable_columns with a custom QuerySet.
                    elif filter_field.is_relation:
                        filterable_column["is_relation"] = filter_field.is_relation

                        # Use the last field from the "lookup" to specify the value for the choice.
                        if filter_field_lookup:
                            lookup = filter_field_lookup.split("__")[-1]
                            choices = [
                                (getattr_or_get(c, lookup, c.pk), c)
                                for c in filter_model.objects.all()
                            ]

                        # If no "lookup" is used, simply use the QuerySet.all() as choices.
                        else:
                            choices = filter_model.objects.all()
                except AttributeError:
                    pass

                # Add an empty label to the choices to allow clearing the filter.
                if choices:
                    filterable_column["choices"] = [("", "---------")] + list(choices)

            #
            # We now know the filter type and choices. Use the request to find the initial value (if set).
            #

            request = context.get("request")
            filterable_column["value"] = request.GET.get(filter_field_key)

        _cache["get_filters"] = filterable_columns
        return filterable_columns

    def get_filter_query_params():
        return create_list_of_dict(config.get("filter_query_params"), "key", "value")

    def get_groups():
        """
        Splits object_list into one or more groups, returns a dict for each group containing:

        - id: a unique id identifying this group.
        - default: whether the group is the default groups (no groups were set).
        - label: the string representation of a group, (rendered as subtitle).
        - lookup: The value for lookup in obj to test groups against, may be a field lookup. Optionally a callable can
          be given in which case it will be called with obj as first argument and the returned value will be used as
          value to test against.
        - value: the resulting value of lookup required to match object to this group.
        - object_list: the objects matching this group.

        :return: list_of_dict.
        """
        groups = parse_kwarg(config, "groups")
        object_list = get_datagrid_object_list()

        if not groups:
            return [
                {
                    "id": get_id({}, "datagrid-group"),
                    "default": True,
                    "label": None,
                    "lookup": None,
                    "value": None,
                    "object_list": object_list,
                }
            ]

        lookup = groups.get("lookup")
        group_defs = groups.get("groups")
        group_defs = create_list_of_dict(group_defs, "value", "label")

        groups = []
        for group_def in group_defs:
            group = {
                "id": get_id({}, "datagrid-group"),
                "default": False,
                "label": group_def.get("label"),
                "lookup": lookup,
                "value": group_def.get("value"),
                "object_list": [
                    obj
                    for obj in object_list
                    if get_lookup_value(obj, lookup) == group_def.get("value")
                ],
            }
            groups.append(group)
        return groups

    def get_lookup_value(obj, lookup):
        """
        Returns the value for lookup in obj to test groups against, may be a field lookup. Optionally a callable can be
        given in which case it will be called with obj as first argument and the returned value will be used as value to
        test against.
        :param obj:
        :param lookup:
        :return:
        """
        if callable(lookup):
            return lookup(obj)
        return get_recursed_field_value(obj, lookup)

    def get_ordering():
        """
        Return the field to use for ordering the queryset.
        Only allows ordering by dict keys found in the orderable_columns option.
        :return: string or None
        """
        if _cache.get("get_ordering"):
            return _cache.get("get_ordering")

        request = context["request"]
        ordering_key = get_ordering_key()
        ordering = request.GET.get(ordering_key)
        orderable_columns = get_orderable_columns()

        result = None
        if ordering and ordering.replace("-", "") in [c.get("lookup") for c in orderable_columns]:
            result = ordering
        elif ordering:
            pass
        _cache["get_ordering"] = result
        return result

    def get_ordering_key():
        """
        Returns the query parameter to use for ordering.
        :return: string
        """
        return parse_kwarg(config, "ordering_key", "ordering")

    def get_orderable_columns():
        """
        Returns the the key and lookup field for every column which should be made ordrable..
        :return: A list_of_dict where each dict contains at least "key" and "lookup" keys.
        """
        if _cache.get("get_orderable_columns"):
            return _cache.get("get_orderable_columns")

        orderable_columns = parse_kwarg(config, "orderable_columns", {})
        orderable_columns_list_of_dict = []

        """
          - If a dict is passed each key will map to a field (the key) in columns, each value will be used to describe
            a field lookup.
            Example: {"author": "author__first_name"}
        """
        if type(orderable_columns) is dict:
            orderable_columns_list_of_dict = [
                {"key": item[0], "lookup": item[1]} for item in orderable_columns.items()
            ]

        """
          - If a list is passed each value will map to a field (the key) in columns and will also be used to describe
            a field lookup
            Example: ['author', 'title']
        """
        if type(orderable_columns) is list or type(orderable_columns) is tuple:
            for orderable_column in orderable_columns:
                if type(orderable_column) is dict:
                    """
                    Edge case: A dict is found within the list, this is also supported.
                    """
                    key = orderable_column["key"]
                    lookup = orderable_column.get(
                        "order_lookup", orderable_column.get("lookup", key)
                    )
                    orderable_column_dict = {"key": key, "lookup": lookup}
                else:
                    orderable_column_dict = {"key": orderable_column, "lookup": orderable_column}

                orderable_columns_list_of_dict.append(orderable_column_dict)

        _cache["get_orderable_columns"] = orderable_columns_list_of_dict
        return orderable_columns_list_of_dict

    def get_ordering_dict():
        """
        Returns a dict containing a dict with ordering information (direction, url) for every orderable column.
        :return: dict
        """
        request = context["request"]
        order_by_index = config.get("order_by_index", False)
        ordering_dict = {}

        try:
            i = 1
            for orderable_column in get_orderable_columns():
                orderable_column_key = orderable_column["key"]
                orderable_column_lookup = orderable_column["lookup"]

                querydict = QueryDict(request.GET.urlencode(), mutable=True)
                ordering_key = get_ordering_key()
                ordering_value = str(i) if order_by_index else orderable_column_lookup
                current_ordering = get_ordering()

                directions = {
                    "asc": ordering_value.replace("-", ""),
                    "desc": "-" + ordering_value.replace("-", ""),
                }

                direction_url = directions["asc"]
                direction = None

                if current_ordering == directions["asc"]:
                    direction = "asc"
                    direction_url = directions["desc"]
                elif current_ordering == directions["desc"]:
                    direction = "desc"
                    direction_url = directions["asc"]

                querydict[ordering_key] = direction_url
                ordering_dict[orderable_column_key] = {
                    "direction": direction,
                    "url": "?" + querydict.urlencode(),
                }

                i += 1
        except AttributeError:
            pass
        return ordering_dict

    def get_form_buttons():
        """
        Gets the buttons to use for the form based on config['form_buttons'].
        :return: A list_of_dict where each dict contains at least "name" and "label" keys.
        """
        form_buttons = parse_kwarg(config, "form_buttons", {})

        # Convert dict to list_of_dict
        try:
            form_buttons = [{"name": key, "label": value,} for key, value in form_buttons.items()]
        except AttributeError:
            pass

        for form_button in form_buttons:
            form_button["form"] = form_button.get(
                "form", f"datagrid-action-form-{get_datagrid_id(config)}"
            )

        return form_buttons

    def get_form_select():
        """
        Gets the select to use for the form based on config['form_select'] and form_options.
        :return: A dict with at least "name" and "options" keys, options is a list_of_dict.
        """
        form_select = parse_kwarg(config, "form_select", None)
        if form_select:
            form_options = parse_kwarg(config, "form_options", [])
            form_select["class"] = form_select.get("class", "")
            form_select["choices"] = [get_option(o) for o in form_options]
            form_select["form"] = f"datagrid-action-form-{get_datagrid_id(config)}"
            return form_select

        return None

    def get_option(option):
        """
        Converts an option dict ("label", "value") to choice tuple.
        :param option: dicts
        :return: tuple
        """
        label = option.get("label")
        value = option.get("value")
        return value, label

    def get_formset():
        """
        :return: BaseModelFormSet
        """
        request = context.get("request")
        form_class = config.get("form_class")
        formset_valid = config.get("formset_valid")
        model = get_model(context, config)
        object_list = get_datagrid_object_list()

        if not (form_class and model):
            return

        pks = [o.pk for o in object_list]
        queryset = model.objects.filter(pk__in=pks)

        ModelFormSet = modelformset_factory(model, form_class, extra=0)
        if request.method == "POST":
            formset = ModelFormSet(request.POST)

            if formset.is_valid():
                instances = formset.save()
                # Reset the cache for fresh data
                _cache.clear()
                if formset_valid:
                    formset_valid(request, instances)
                return ModelFormSet(queryset=queryset.all())
            else:
                return formset
        result = ModelFormSet(queryset=queryset)
        return result

    def add_paginator(object_list):
        """
        Return datagrid_context with added paginator configuration.
        :param object_list:
        """
        config["is_paginated"] = config.get("is_paginated", context.get("is_paginated"))

        if config.get("paginate"):
            """
            Paginate object_list.
            """
            request = context["request"]
            paginate_by = config.get("paginate_by", 100)
            paginator = Paginator(object_list, paginate_by)
            page_key = config.get("page_key", "page")
            page_number = request.GET.get(page_key, 1)

            if str(page_number).upper() == "LAST":
                page_number = paginator.num_pages

            page_obj = paginator.get_page(page_number)
            object_list = page_obj.object_list

            config["is_paginated"] = True
            config["paginator"] = paginator
            config["page_key"] = page_key
            config["page_number"] = page_number
            config["page_obj"] = page_obj
            config["object_list"] = object_list

        if config.get("is_paginated"):
            """
            Rely on view/context for pagination.
            """
            config["paginator"] = config.get("paginator", context.get("paginator"))
            config["page_key"] = config.get("page_key", "page")
            config["page_number"] = config.get("page_number")
            config["page_obj"] = config.get("page_obj", context.get("page_obj"))

        return object_list

    def add_object_attributes(datagrid_context):
        """
        Calls add_display(obj) and add_modifier_class(obj) for every obj in (paginated) object_list.
        :param datagrid_context:
        :return: datagrid_context
        """
        object_list = get_datagrid_object_list()

        for obj in object_list:
            add_display(obj)
            add_modifier_class(obj)
        return datagrid_context

    def add_display(obj):
        """
        If a get_<field>_display callable is set, add the evaluated result to the rh_display_<field> field on the
        object passed to obj.
        :param obj:
        """
        for column in get_columns():
            key = column["key"]
            fn = config.get("get_{}_display".format(key), None)
            if fn:
                setattr(obj, "rh_display_{}".format(key), fn(obj))

    def add_modifier_class(obj):
        """
        If a modifier configuration is set, add the result color as datagrid_modifier_class to the object passed to
        obj.
        :param obj:
        """
        try:
            key = parse_kwarg(config, "modifier_key", None)

            if not key:
                return

            modifier_map = parse_kwarg(config, "modifier_mapping", {})
            object_value = getattr(obj, key)

            for item_key, item_value in modifier_map.items():
                pattern = re.compile(item_key)
                if pattern.match(str(object_value)):
                    obj.datagrid_modifier_class = item_value
        except KeyError:
            pass

    def get_export_buttons():
        """
        Returns a list of dict with button configurations for each button in export_buttons.
        """
        export_buttons = parse_kwarg(config, "export_buttons")
        export_buttons = create_list_of_dict(export_buttons, "name", "value")

        for export_button in export_buttons:
            class_name = export_button.get("class")
            value = export_button.get("value")

            export_button[
                "class"
            ] = f"button--icon-right button--light button--small datagrid__export datagrid__export--{value} {class_name}".strip()
            export_button["far_icon"] = export_button.get("far-icon", f"file-{value}")
            export_button["label"] = export_button.get("label", _("Exporteer"))
            export_button["form"] = export_button.get(
                "form", f"datagrid-action-form-{get_datagrid_id(config)}"
            )

        return export_buttons

    config = merge_config(kwargs)

    # i18n
    config["label_filter_placeholder"] = parse_kwarg(
        config, "label_filter_placeholder", _("Filter resultaten")
    )
    config["label_no_results"] = parse_kwarg(config, "label_no_results", _("Geen resultaten"))
    config["label_result_count"] = parse_kwarg(config, "label_result_count", _("resultaten"))
    config["label_select_all"] = parse_kwarg(config, "label_select_all", _("(De)selecteer alles"))

    # Formset modifies data so goes first
    config["formset_valid"] = config.get("formset_valid", "")
    config["formset"] = get_formset()

    # Showing Data/Filtering/Grouping/Ordering
    config["columns"] = get_columns()
    config["object_list"] = get_datagrid_object_list(
        config.get("formset") and context.get("request").method == "POST"
    )
    config["filters"] = get_filters()
    config["filter_action"] = config.get("filter_action")
    config["filter_query_params"] = get_filter_query_params()
    config["groups"] = get_groups()
    config["dom_filter"] = parse_kwarg(config, "dom_filter", False)
    config["ordering"] = get_ordering_dict()

    # Manipulating data (form)
    config["form"] = (
        parse_kwarg(config, "form", False)
        or bool(config.get("form_action"))
        or bool(config.get("form_buttons"))
    )
    config["form_action"] = config.get("form_action", "")
    config["form_method"] = parse_kwarg(config, "form_method", "post")
    config["form_buttons"] = get_form_buttons()
    config["form_checkbox_name"] = config.get("form_checkbox_name", "objects")
    config["form_select_all_position"] = config.get("form_select_all_position", "top")
    config["form_select"] = get_form_select()
    config["form_model_name"] = config.get("form_model_name", "model")
    config["form_model_meta_label"] = get_model_label(context, config)

    config["toolbar_position"] = config.get("toolbar_position", "top")

    # Custom presentation (get_<field>_display)/Color coded rows
    config = add_object_attributes(config)
    config["modifier_column"] = get_modifier_column()

    # Export
    config["export_buttons"] = get_export_buttons()
    config["export_input_name"] = config.get("export_input_name", "fields")

    # Additional options
    config["class"] = config.get("class", None)
    config["id"] = get_datagrid_id(config)
    config["title"] = config.get("title", None)
    config["url_reverse"] = config.get("url_reverse", "")
    config["urlize"] = config.get("urlize", True)
    config["urlizetrunc"] = config.get("urlizetrunc")

    # Context
    config["request"] = context["request"]
    config["config"] = config
    return config
