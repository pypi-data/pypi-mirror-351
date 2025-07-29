from jinja2 import Environment, meta


def extract_jinja_variables(template_str):
    env = Environment()
    parsed_template = env.parse(template_str)
    return meta.find_undeclared_variables(parsed_template)
