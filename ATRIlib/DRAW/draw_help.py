from jinja2 import Environment, FileSystemLoader, select_autoescape

from ATRIlib.Config import path_config
from ATRIlib.DRAW.html_renderer import render_html_to_jpeg

HELP_WIDTH = 1600

HELP_TEMPLATE_DIR = path_config.help_template_file_path.resolve().parent

env = Environment(
    loader=FileSystemLoader(HELP_TEMPLATE_DIR),
    autoescape=select_autoescape(("html", "xml")),
)


def draw_help(help_data):
    template = env.get_template(path_config.help_template_file_path.name)
    context = dict(help_data)
    context["atri_uri"] = path_config.help_atri_file_path.resolve().as_uri()
    html_content = template.render(**context)
    return render_html_to_jpeg(html_content, width=HELP_WIDTH)
