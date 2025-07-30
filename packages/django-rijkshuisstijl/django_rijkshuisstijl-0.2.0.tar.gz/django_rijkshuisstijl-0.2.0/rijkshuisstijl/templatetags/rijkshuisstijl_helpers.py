import json
from uuid import uuid4

from django.utils.safestring import SafeText

try:
    from json import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError


#
# Template tag partials.
#


def get_id(config, prefix):
    """
    Gets the id to put on the component based on config["id"], if no id is provided a uuid4 is created and prefixed
    with "<prefix>-".
    :return: A str which should be unique to this template tag.
    """
    return config.get("id", prefix + "-" + str(uuid4()))


def get_model(context, config):
    """
    Returns the Model of the QuerySet (if passed).
   :param context: Template tag context.
     :param config: Template tag configuration.
    :return: Model or None.
    """
    # Get model from config.
    model = config.get("model")

    if not model:
        # Get model from QuerySet.
        try:
            model = get_object_list(context, config).model
        except AttributeError:
            pass

    if not model:
        # Get model from form_class.
        try:
            model = config.get("form_class")._meta.model
        except AttributeError:
            pass

    return model


def get_model_label(context, config):
    """
    Returns the _meta.label of the Model of the QuerySet (if passed).
    :param context: Template tag context.
    :param config: Template tag configuration.
    :return: str or None.
    """
    model_label = None

    try:
        model_label = get_model(context, config)._meta.label
    except AttributeError:
        pass

    return model_label


def get_object_list(context, config):
    """
    Looks for the object_list to use based on the presence of these variables in order:

        1) config['queryset']
        2) config['object_list']
        3) context['queryset']
        4) context['object_list']

    :param context: Template tag context.
    :param config: Template tag configuration.
    :return: QuerySet or list.
    """
    context_object_list = context.get("object_list", [])
    context_queryset = context.get("queryset", context_object_list)
    object_list = config.get("object_list", context_queryset)
    object_list = config.get("queryset", object_list)

    return object_list


def get_queryset(context, config):
    """
    Returns the QuerySet (if passed).
    :param context: Template tag context.
    :param config: Template tag configuration.
    :return: QuerySet or None.
    """
    queryset = None

    if get_model(context, config):
        queryset = get_object_list(context, config)

    return queryset


#
# Utility functions.
#


def get_config_from_prefix(config, prefix):
    """
    Creates a new "config" from kwargs, only for keys that start with prefix.
    Strips prefix from resulting dict keys.
    Strips leading underscore ("_") from dict keys.
    :param config: A dict, possibly output from get_config().
    :param prefix: A str, the prefix (without trailing underscore) to filter config on.
    :return: dict
    """
    return {
        key[len(prefix) + 1:]: value
        for key, value in config.items()
        if key.startswith(prefix)
    }


def create_list_of_dict(obj, name_key="key", name_value="label"):
    """
    Converts obj to a list_of_dict containing name_key and name_value for every dict.
    Obj can be dict, string or list.

    Output format (name_key="key", name_value="label"):

        [{"key": "foo", "label": "bar"}]

    :param obj: Value to convert
    :param name_key: Name for the key in every dict.
    :param name_value: Name for the value in every dict.
    :return: list_of_dict
    """
    try:
        # Convert dict to list_of_dict.
        return [{name_key: key, name_value: value} for key, value in obj.items()]
    except AttributeError:
        list_of_dict = []

        # Convert string to list_of_dict.
        if type(obj) == str or type(obj) == SafeText:
            return [{name_key: obj, name_value: obj}]

        # Convert list to list_of_dict.
        elif type(obj) is list or type(obj) is tuple:
            for column in obj:
                # Already dict
                if type(column) == dict:
                    list_of_dict.append(column)
                # Not dict
                else:
                    list_of_dict.append({name_key: column, name_value: column})
        return list_of_dict


def get_model_from_obj(obj):
    """
    Tries to return a model based on obj.
    :param obj: A model instance or a QuerySet.
    :return: The found model class or None.
    """
    try:
        return obj._meta.model
    except AttributeError:
        return obj.model
    except:
        return None


def get_request_user(request):
    """
    Safely get request.user
    :param request: A http request
    :return: A user instance if found on request or else an AnonymousUser
    """
    if hasattr(request, 'user'):
        return request.user
    else:
        from django.contrib.auth.models import AnonymousUser
        return AnonymousUser()


def merge_config(kwargs):
    """
    Merges "config" and other items in kwarg to generate configuration dict.
    Other kwargs override items in config.
    :param kwargs: (optional) dict in in kwargs mirroring other kwargs.
    :return: A merged dict containing configuration.
    """
    config = kwargs.pop("config", {})
    _kwargs = config.copy()
    _kwargs.update(kwargs)
    kwargs = _kwargs

    return kwargs


def parse_arg(arg, default=None):
    """
    Parses an argument (or value in kwargs)

    Syntax::

        Comma separated:
        - dict (Key value): "foo:bar,bar:baz" -> {'foo': 'bar', 'bar: 'baz')
        - list: "foo,bar,baz" -> ['foo, 'bar', baz']
        - string: "foo": "foo"

        JSON:
        - "[{"foo": "bar"}, {"bar": "baz"}]" -> [{'foo': 'bar'}, {'bar: 'baz')]

        Edge case:
        Given a dict as default ({}) list is converted into matching pair dict:
        - parse_arg("foo,bar,baz", {}) -> {'foo': 'foo', 'bar': 'bar', 'baz': 'baz}

        Given None returns default:
        - None -> default

        Given a non-string arg returns value directly.
        - True -> True

    :param arg: The input value to parse.
    :param default: Returned when arg is None.
    :return: The parsed arg.
    """
    if arg is None:
        return default

    if type(arg) != str and type(arg) != SafeText:
        return arg

    if arg == "True":
        return True
    if arg == "False":
        return False

    if "," in arg or ":" in arg:

        # Parse JSON.
        try:
            return json.loads(arg)
        except JSONDecodeError:
            pass

        # Parse list (comma separated).
        lst = [entry.strip() for entry in arg.strip().split(",") if entry]

        # Parse flat dict (each item in lst, colon separated).
        if ":" in arg or isinstance(default, dict):
            dct = {}
            for value in lst:
                try:
                    key, val = value.split(":")
                except ValueError:
                    key = value
                    val = value
                dct[key] = val or key
            return dct  # Flat dict
        return lst  # List
    return arg


def parse_kwarg(kwargs, name, default=None):
    """
    Parses value of name of kwargs.
    See parse_arg for syntax of value.

    :param kwargs:  Dict containing key name.
    :param name: The key in kwargs to parse.
    :param default: The default value if the kwargs[name] is None.
    :return: The parsed value of kwargs[name].
    """
    value = kwargs.get(name, default)
    return parse_arg(value, default)
