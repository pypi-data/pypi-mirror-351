from django.forms.widgets import CheckboxInput, DateInput, Input, Select, Widget
from django.utils.translation import gettext_lazy as _

from rijkshuisstijl.conf import settings
from rijkshuisstijl.templatetags.rijkshuisstijl import register

from .rijkshuisstijl_helpers import get_id, merge_config, parse_kwarg


@register.inclusion_tag("rijkshuisstijl/components/button/button.html")
def button(**kwargs):
    config = merge_config(kwargs)

    # kwargs
    config["class"] = config.get("class", None)
    config["far_icon"] = config.get("far_icon", None)
    config["fas_icon"] = config.get("fas_icon", None)
    config["icon"] = config.get("icon", None)
    config["icon_src"] = config.get("icon_src", None)
    config["id"] = config.get("id", None)
    config["label"] = config.get("label", None)
    config["title"] = config.get("title", config.get("label"))
    config["toggle_target"] = config.get("toggle_target", None)
    config["toggle_modifier"] = config.get("toggle_modifier", None)
    config["type"] = config.get("type", None)
    config["name"] = config.get("name", None)
    config["value"] = config.get("value", None)

    config["config"] = config
    return config


@register.inclusion_tag("rijkshuisstijl/components/button/link.html")
def button_link(**config):
    config = merge_config(config)

    config["class"] = config.get("class", None)
    config["far_icon"] = config.get("far_icon", None)
    config["fas_icon"] = config.get("fas_icon", None)
    config["icon"] = config.get("icon", None)
    config["icon_src"] = config.get("icon_src", None)
    config["href"] = config.get("href", "")
    config["target"] = config.get("target", None)
    config["label"] = config.get("label", None)
    config["title"] = config.get("title", config.get("label"))
    config["config"] = config
    return config


@register.inclusion_tag("rijkshuisstijl/components/form/form.html", takes_context=True)
def form(context, form=None, label="", **kwargs):
    config = merge_config(kwargs)

    config["form"] = form or parse_kwarg(config, "form", context.get("form"))
    config["action"] = config.get("action")
    config["compact"] = config.get("compact")
    config["disabled"] = config.get("disabled")
    config["label"] = config.get("label", label)
    config["title"] = config.get("title")
    config["subtitle"] = config.get("subtitle")
    config["text"] = config.get("text")
    config["urlize"] = config.get("urlize")
    config["wysiwyg"] = config.get("wysiwyg")
    config["status"] = config.get("status")
    config["intro_status"] = config.get("intro_status")
    config["tag"] = config.get("tag", "form")
    config["actions"] = parse_kwarg(config, "actions", [])  # TODO: Default action
    config["actions_align"] = config.get("actions_align", "left")
    config["actions_position"] = config.get("actions_position", "auto")
    config["help_text_position"] = config.get("help_text_position", settings.RH_HELP_TEXT_POSITION)

    config["request"] = context["request"]
    config["config"] = config
    return config


@register.inclusion_tag(
    "rijkshuisstijl/components/confirm-form/confirm-form.html", takes_context=True
)
def confirm_form(context, **kwargs):
    def get_object_list():
        context_object_list = context.get("object_list", [])
        context_queryset = context.get("queryset", context_object_list)
        object_list = config.get("object_list", context_queryset)
        object_list = config.get("queryset", object_list)
        return object_list

    config = merge_config(kwargs)

    # i18n
    config["label_confirm"] = parse_kwarg(config, "label_confirm", _("Bevestig"))

    # kwargs
    config["id"] = get_id(config, "confirm-form")
    config["class"] = config.get("class", None)
    config["method"] = config.get("method", "post")
    config["object_list"] = get_object_list()
    config["name_object"] = config.get("name_object", "object")
    config["name_confirm"] = config.get("name_confirm", "confirm")
    config["status"] = config.get("status", "warning")
    config["title"] = config.get("title", _("Actie bevestigen"))
    config["text"] = config.get("text", _("Weet u zeker dat u deze actie wilt uitvoeren?"))

    config["config"] = config
    return config


@register.inclusion_tag("rijkshuisstijl/components/form/form-control.html", takes_context=True)
def form_control(context, form, field_name, **kwargs):
    """
    Rendes a form control for field "field_name" in form.
    :param form: A (Django) form.
    :param field_name: The name of the field in form.
    :return:
    """
    config = merge_config(kwargs)
    kwargs["form"] = form or parse_kwarg(kwargs, "form", context.get("form"))
    kwargs["action"] = kwargs.get("action")
    kwargs["compact"] = kwargs.get("compact")
    kwargs["label"] = kwargs.get("label", label)
    kwargs["title"] = kwargs.get("title")
    kwargs["subtitle"] = kwargs.get("subtitle")
    kwargs["text"] = kwargs.get("text")
    kwargs["urlize"] = kwargs.get("urlize")
    kwargs["wysiwyg"] = kwargs.get("wysiwyg")
    kwargs["status"] = kwargs.get("status")
    kwargs["intro_status"] = kwargs.get("intro_status")
    kwargs["tag"] = kwargs.get("tag", "form")
    kwargs["actions_align"] = kwargs.get("actions_align", "left")
    kwargs["actions_position"] = kwargs.get("actions_position", "auto")
    kwargs["help_text_position"] = kwargs.get("help_text_position", settings.RH_HELP_TEXT_POSITION)

    def get_bound_field():
        """
        Returns the BoundField.
        :return: BoundField
        """

        if isinstance(field_name, str):
            return form[field_name]
        return field_name

    config["form"] = form
    config["bound_field"] = _field(get_bound_field())
    config["help_text_position"] = config.get("help_text_position", "bottom")
    config["config"] = config
    return config


@register.inclusion_tag("rijkshuisstijl/components/form/label.html")
def label(**kwargs):
    kwargs = merge_config(kwargs)
    kwargs["help_text_position"] = kwargs.get("help_text_position", settings.RH_HELP_TEXT_POSITION)
    kwargs["config"] = kwargs
    return kwargs


@register.inclusion_tag("rijkshuisstijl/components/form/help-text.html")
def help_text(help_text, **kwargs):
    kwargs = merge_config(kwargs)
    kwargs["config"] = kwargs
    kwargs["for"] = kwargs.get("for")
    kwargs["help_text"] = kwargs.get("help_text", help_text)
    return kwargs


@register.inclusion_tag("rijkshuisstijl/components/form/field.html")
def form_field(form, field_name, **kwargs):
    """
    Renders a form field
    :param form: A (Django) form.
    :param field_name: The name of the field in form.
    :param kwargs: Any kwargs will passed as "attr" in the fields widgets.
    """
    config = merge_config(kwargs)

    def get_bound_field():
        """
        Returns the BoundField.
        :return: BoundField
        """

        if isinstance(field_name, str):
            return form[field_name]
        return field_name

    def get_extra_attrs():
        """
        Returns additional attrsibutes for the field widget.
        :return: dict
        """
        return parse_kwarg(config, "attrs", {})

    config["attrs"] = get_extra_attrs()
    config["form"] = form
    config["bound_field"] = _field(get_bound_field(), **get_extra_attrs())
    config["config"] = config
    return config


@register.inclusion_tag("rijkshuisstijl/components/form/field.html")
def form_input(**kwargs):
    config = merge_config(kwargs)
    return _form_widget(Input, {}, **config)


@register.inclusion_tag("rijkshuisstijl/components/form/field.html")
def form_checkbox(**kwargs):
    config = merge_config(kwargs)
    checked = parse_kwarg(config, "checked", False)
    return _form_widget(CheckboxInput, {"check_test": lambda v: checked}, **config)


@register.inclusion_tag("rijkshuisstijl/components/form/field.html")
def form_select(**kwargs):
    config = merge_config(kwargs)
    return _form_widget(Select, {}, **config)


def _form_widget(Widget, widget_config, **config):
    name = config.get("name", "")
    value = config.get("value", "")
    widget = Widget(attrs=config, **widget_config)
    config["bound_field"] = _field(widget).render(name, value)
    config["config"] = config
    return config


def _field(bound_field, **extra_attrs):
    def get_widget(bound_field):
        """
        Returns the widget.
        :param bound_field:
        :return:
        """
        widget = bound_field

        try:
            field = bound_field.field
            widget = field.widget
        except AttributeError:
            pass

        if isinstance(widget, Widget):
            return widget

    def add_choices(bound_field):
        """
        Adds choices to widget..
        :param bound_field:
        :return: BoundField
        """
        widget = get_widget(bound_field)

        if not widget:
            return

        # Make model objects work as choice.
        try:
            choices = widget.attrs.pop("choices")
            if choices:

                serialized_choices = []
                for choice in choices:
                    try:
                        choice._meta.model  # noqa
                        choice = (choice.pk, str(choice))
                    except AttributeError:
                        pass

                    serialized_choices.append(choice)
                widget.choices = serialized_choices
        except KeyError:
            pass

        return bound_field

    def add_attrs(bound_field):
        """
        Adds additional "kwargs" as "attrs" to widget.
        :param bound_field: BoundField
        :return: BoundField
        """

        # Get widget.
        widget = get_widget(bound_field)

        if not widget:
            return

        # Copy mark_required.
        try:
            mark_required = getattr(bound_field.field, "mark_required", False)
        except AttributeError:
            mark_required = getattr(bound_field, "mark_required", False)

        if mark_required:
            widget.attrs["data-mark-required"] = str(mark_required)

        if widget.is_required or "data-mark-required" in widget.attrs:
            if not widget.attrs.get("title"):
                widget.attrs["title"] = _("Dit veld is verplicht.")

        # Use ISO input formats for DateInput.
        if isinstance(widget, DateInput):
            widget.format = "%Y-%m-%d"

        attrs = {**widget.attrs, **extra_attrs}

        html_attrs = {k.replace("_", "-"): v for k, v in attrs.items() if v}
        widget.attrs = html_attrs
        return bound_field

    def replace_template_paths(bound_field):
        """
        Replaces the default (Django) template paths by the ones provided by django-rijkshuisstijl.
        :param bound_field: BoundField
        :return: BoundField
        """
        bound_field = replace_template_path(bound_field, "template_name")
        return replace_template_path(bound_field, "option_template_name")

    def replace_template_path(bound_field, property):
        """
        Replaces the default (Django) template path in property by the one provided by django-rijkshuisstijl.
        :param bound_field: BoundField
        :return: BoundField
        """
        try:
            field = bound_field.field
            widget = field.widget
        except AttributeError:
            widget = bound_field

        try:
            template_name = getattr(widget, property)

            if not "django" in template_name:
                return bound_field

            template_split = template_name.split("/")
            template_file = template_split[-1]
            setattr(widget, property, f"rijkshuisstijl/components/form/widgets/{template_file}")
        except AttributeError:
            pass

        return bound_field

    return replace_template_paths(add_attrs(add_choices(bound_field)))
