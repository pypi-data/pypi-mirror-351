from django.template.defaultfilters import urlize
from django.utils.safestring import mark_safe

from bs4 import BeautifulSoup
from rijkshuisstijl.templatetags.rijkshuisstijl import register


@register.filter
def get(value, key):
    """
    Gets a value from a dict by key.
    Returns empty string on failure.
    :param value: A dict containing key.
    :return: The key's value or ''.
    """
    try:
        return value[key]
    except:
        return ""


@register.filter
def getattr_or_get(value, key, default=""):
    """
    Gets an attribute from an object or a value from a dict by key.
    Returns empty string on failure.
    :param value: An object or dict containing key.
    :return: The key's value or ''.
    """
    try:
        return getattr(value, key, default)
    except AttributeError:
        return get(value, key, default)
    except:
        return default


@register.filter
def rh_urlize(value, target=None):
    html = urlize(value)
    soup = BeautifulSoup(html, "html.parser")
    anchors = soup.find_all("a")
    for anchor in anchors:
        if target:
            anchor["target"] = target
    return mark_safe(str(soup))
