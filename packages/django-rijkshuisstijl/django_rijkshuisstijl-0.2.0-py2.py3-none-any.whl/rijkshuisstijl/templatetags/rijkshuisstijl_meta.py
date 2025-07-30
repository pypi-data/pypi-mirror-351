from rijkshuisstijl.templatetags.rijkshuisstijl import register


@register.inclusion_tag("rijkshuisstijl/components/meta/meta-css.html")
def meta_css():
    """
    Add the CSS stylesheet to the template.

    Example:

        {% meta_css %}
    """


@register.inclusion_tag("rijkshuisstijl/components/meta/meta-js.html")
def meta_js():
    """
    Add the JavaScript entrypoint to the template.

    Example:

        {% meta_js %}
    """


@register.inclusion_tag("rijkshuisstijl/components/meta/meta-icons.html")
def meta_icons():
    """
    Add the web icons to the template.

    Example:

        {% meta_icons %}
    """
