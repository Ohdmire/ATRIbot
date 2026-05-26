import html
import re
from copy import deepcopy

from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader, select_autoescape

from ATRIlib.Config import path_config
from ATRIlib.DRAW.html_renderer import render_html_to_png

MEDAL_WIDTH = 966
PROJECT_ROOT = path_config.medal_html_template_file_path.resolve().parents[2]
TEMPLATE_DIR = path_config.medal_html_template_file_path.resolve().parent
FONT_PATH = (PROJECT_ROOT / "assets/fonts/ttf/Torus-Regular.ttf").resolve()


env = Environment(
    loader=FileSystemLoader(TEMPLATE_DIR),
    autoescape=select_autoescape(("html", "xml")),
)


def _gamemode_name(gamemode):
    return {
        "osu": "Standard",
        "fruits": "Catch",
        "mania": "Mania",
        "taiko": "Taiko",
    }.get(gamemode, gamemode)


def _plain_text(value):
    if value is None:
        return None
    text = (
        html.unescape(str(value))
        .replace("<br>", "\n")
        .replace("<br/>", "\n")
        .replace("<br />", "\n")
    )
    text = BeautifulSoup(text, "html.parser").get_text("\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() or None


def _icon_src(medal):
    local_icon = (path_config.medal_path / f"{medal['Medal_ID']}.png").resolve()
    if local_icon.exists():
        return local_icon.as_uri()
    raise FileNotFoundError(f"medal {medal['Medal_ID']} 本地图标不存在: {local_icon}")


def _notes(medal):
    notes = []
    mods = _plain_text(medal.get("Mods"))
    packs = _plain_text(medal.get("Packs"))

    if mods:
        notes.append({"kind": "allowed", "text": f"允许的模组: {mods}."})
    if packs:
        notes.append({"kind": "required", "text": f"需要图包: {packs}."})

    gamemode = medal.get("Gamemode")
    if gamemode and gamemode != "all":
        mode_name = _gamemode_name(gamemode)
        notes.append(
            {"kind": "restricted", "text": f"这个奖牌只能在 {mode_name} 模式中获取."}
        )
    # if medal.get("Is_Restricted"):
    #     notes.append({"kind": "restricted", "text": "This medal is restricted."})

    return notes


def _frequency_text(medal):
    frequency = medal.get("Frequency")
    if frequency is None:
        return None
    return f"{float(frequency) * 100:.2f}% achieved"


def draw_medal_html(medal, output_path=None):
    medal = deepcopy(medal)
    medal.pop("_id", None)
    for key in (
        "Name",
        "Description",
        "Instructions",
        "Solution",
        "Grouping",
        "Gamemode",
    ):
        medal[key] = _plain_text(medal.get(key))

    medal["icon_src"] = _icon_src(medal)
    medal["notes"] = _notes(medal)
    medal["frequency_text"] = _frequency_text(medal)
    medal["gamemode_text"] = _gamemode_name(medal.get("Gamemode"))

    template = env.get_template(path_config.medal_html_template_file_path.name)
    html_content = template.render(
        medal=medal,
        font_src=FONT_PATH.as_uri(),
    )
    if output_path is None:
        output_path = path_config.medal_result_path / f"{medal['Medal_ID']}.png"

    return render_html_to_png(
        html_content,
        width=MEDAL_WIDTH,
        output_path=output_path,
        base_url=PROJECT_ROOT,
    )
