import yaml
from jinja2 import Environment, loaders
from jinja2.runtime import StrictUndefined, Undefined
from jinja2.ext import Extension
from jinja2.lexer import Token
from io import StringIO


class YAMLEverythingExtension(Extension):
    """
    Insert a `|yaml` filter at the end of every variable substitution.
    This will ensure that all injected values are converted to a YAML-escaped value, thus preventing
    YAML injection.
    """

    def filter_stream(self, stream):
        for token in stream:
            if token.type == "variable_end":
                yield Token(token.lineno, "pipe", "|")
                yield Token(token.lineno, "name", "yaml")
            yield token


def yaml_filter(val):
    """
    Serialize some value in isolation, not as part of any document.
    We can't just use yaml.dump because that outputs an entire document, including newlines, which
    isn't helpful for inserting into a YAML document.
    """
    # in strict mode, reject undefined variables
    if isinstance(val, StrictUndefined):
        val._fail_with_undefined_error()

    # in lax mode, render nulls
    elif isinstance(val, Undefined):
        val = None

    stream = StringIO()
    dumper = yaml.dumper.Dumper(stream)
    dumper.open()
    node = dumper.represent_data(val)
    dumper.serialize(node)
    # The serialized node tends to have a \n at the end.  The template might not
    # want a \n inserted here, e.g. if two variables are on the same line, so
    # strip.
    return stream.getvalue().strip()


def get_environment(undefined=StrictUndefined):
    """
    Create a standard Jinja environment that has everything we need in it.
    """
    jinja_env = Environment(
        extensions=(YAMLEverythingExtension,),
        loader=loaders.FileSystemLoader([".", "/"]),
        undefined=undefined,
    )
    jinja_env.filters["yaml"] = yaml_filter
    return jinja_env


def safe_jinja_yaml_render(yaml_template, allow_undefined_variables=False, **params):
    """
    Renders a yaml template string using provided params.
    All params will be automatically encoded as yaml values, preventing yaml code injection, by
    entering newlines in values for example.
    """
    undefined = StrictUndefined
    if allow_undefined_variables:
        undefined = Undefined
    template = get_environment(undefined=undefined).from_string(yaml_template)
    return template.render(**params)
