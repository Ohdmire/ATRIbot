from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from ATRIlib.Config import path_config
from ATRIlib.DRAW.html_renderer import render_html_to_png


USER_MEDALS_WIDTH = 1000
PROJECT_ROOT = path_config.medal_html_template_file_path.resolve().parents[2]
TEMPLATE_DIR = (PROJECT_ROOT / "assets/templates").resolve()
FONT_PATH = (PROJECT_ROOT / "assets/fonts/ttf/Torus-Regular.ttf").resolve()


env = Environment(
    loader=FileSystemLoader(TEMPLATE_DIR),
    autoescape=select_autoescape(("html", "xml")),
)


def _icon_src(medal_id):
    icon_path = (path_config.medal_path / f"{medal_id}.png").resolve()
    if icon_path.exists():
        return icon_path.as_uri()
    return None


async def draw_user_medals_html(userstruct, medals, output_path=None):
    if output_path is None:
        output_path = path_config.medal_pr_result_path / f"{userstruct['id']}.png"

    view_medals = [
        {
            "id": medal["id"],
            "name": medal.get("name"),
            "achieved_at": medal.get("achieved_at"),
            "icon_src": _icon_src(medal["id"]),
        }
        for medal in medals
    ]

    template = env.get_template("user_medals.html")
    html_content = template.render(
        username=userstruct.get("username", userstruct["id"]),
        medals=view_medals,
        font_src=FONT_PATH.as_uri(),
    )
    return render_html_to_png(
        html_content,
        width=USER_MEDALS_WIDTH,
        output_path=Path(output_path),
        base_url=PROJECT_ROOT,
    )
