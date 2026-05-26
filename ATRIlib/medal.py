import copy
import hashlib
import io
import json
import logging
import re

import aiohttp

from ATRIlib.API.deepseek import translate_with_prompt
from ATRIlib.Config import path_config
from ATRIlib.DB.Mongodb import db_medal, db_user
from ATRIlib.DB.pipeline_medal import (
    get_medal_list_from_db,
    get_user_medal_list_from_db,
    get_user_special_medal_list_from_db,
)
from ATRIlib.DRAW.draw_medal import draw_medal_pr
from ATRIlib.DRAW.draw_medal_html import draw_medal_html
from ATRIlib.TOOLS.Download import download_medal_async

OSEKAI_MEDALS_API = "https://inex.osekai.net/medals/"
OSEKAI_MEDAL_ASSET_BASE_URL = "https://inex.osekai.net/assets/osu/web"
MEDAL_TRANSLATE_SYSTEM_PROMPT = """你是 osu! 成就(medal)奖牌说明的中文翻译助手。
只输出译文，不要解释，不要添加引号。
保留 osu!、Stable、Lazer、mod 缩写、谱面标题、用户名、URL 和数字。
术语约定：beatmap 翻译为谱面，mods 翻译为模组，combo 翻译为连击，pass 翻译为通过，FC 保持 FC。
如果文本是短句、说明或解法，保持原文语气并翻译成自然简洁的中文。"""
MEDAL_TRANSLATE_FIELDS = ("Description", "Instructions", "Solution")


def _plain_text(value):
    if value is None:
        return None
    text = (
        str(value).replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n")
    )
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() or None


def _medal_hash(medal):
    medal_for_hash = copy.deepcopy(medal)
    medal_for_hash.pop("_id", None)
    raw = json.dumps(medal_for_hash, ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def _read_cached_image(cache_file):
    with open(cache_file, "rb") as f:
        img_byte_arr = io.BytesIO(f.read())
    img_byte_arr.seek(0)
    logging.info(f"返回medal缓存: {cache_file}")
    return img_byte_arr


def _translate_medal(medal):
    translated = copy.deepcopy(medal)
    translated.pop("_id", None)

    name = _plain_text(translated.get("Name"))
    if name:
        translated_name = translate_with_prompt(name, MEDAL_TRANSLATE_SYSTEM_PROMPT)
        if translated_name and translated_name != name:
            translated["Name"] = f"{name}（{translated_name}）"
        else:
            translated["Name"] = name

    for field in MEDAL_TRANSLATE_FIELDS:
        text = _plain_text(translated.get(field))
        if not text:
            translated[field] = text
            continue
        translated[field] = translate_with_prompt(text, MEDAL_TRANSLATE_SYSTEM_PROMPT)

    return translated


def calculate_medal(medalid, cache=True):

    medalstrct = get_medal_list_from_db(int(medalid))

    if not medalstrct:
        raise ValueError(f"无法在数据库中找到{medalid}的数据")

    medal = medalstrct[0]
    medal_hash = _medal_hash(medal)
    cache_file = path_config.medal_result_path / f"{int(medalid)}-{medal_hash}.png"

    if cache and cache_file.exists():
        return _read_cached_image(cache_file)

    raw = draw_medal_html(_translate_medal(medal), output_path=cache_file)

    return raw


async def calculate_medal_pr(user_id):

    medalprstrct = get_user_medal_list_from_db(user_id)

    userstruct = db_user.find_one({"id": user_id})

    if not userstruct:
        raise ValueError(f"无法在数据库中找到{user_id}的数据")

    raw = await draw_medal_pr(medalprstrct, userstruct)

    return raw


async def calculate_uu_medal(user_id):

    specialmedalprstrct = get_user_special_medal_list_from_db(user_id)

    medal_Value = {
        55: "🟢1*Pass",
        56: "🟢2*Pass",
        57: "🟢3*Pass",
        58: "🟢4*Pass",
        59: "🟢5*Pass",
        60: "🟢6*Pass",
        61: "🟢7*Pass",
        62: "🟢8*Pass",
        242: "🟢9*Pass",
        244: "🟢10*Pass",
        63: "🟡1*FC",
        64: "🟡2*FC",
        65: "🟡3*FC",
        66: "🟡4*FC",
        67: "🟡5*FC",
        68: "🟡6*FC",
        69: "🟡7*FC",
        70: "🟡8*FC",
        243: "🟡9*FC",
        245: "🟡10*FC",
    }

    result_dict = {}

    for i in specialmedalprstrct:
        result_dict[medal_Value[i["achievement_id"]]] = i["achieved_at"]

    return result_dict


async def calculate_special_medal(user_id):

    specialmedalprstrct = get_user_special_medal_list_from_db(user_id)

    pass_medal_Value = {
        55: "1",
        56: "2",
        57: "3",
        58: "4",
        59: "5",
        60: "6",
        61: "7",
        62: "8",
        242: "9",
        244: "10",
    }

    fc_medal_Value = {
        63: "1",
        64: "2",
        65: "3",
        66: "4",
        67: "5",
        68: "6",
        69: "7",
        70: "8",
        243: "9",
        245: "10",
    }

    result_pass_dict = {}
    result_fc_dict = {}

    for i in specialmedalprstrct:
        if i["achievement_id"] in pass_medal_Value:
            result_pass_dict[pass_medal_Value[i["achievement_id"]]] = i["achieved_at"]
        elif i["achievement_id"] in fc_medal_Value:
            result_fc_dict[fc_medal_Value[i["achievement_id"]]] = i["achieved_at"]

    return result_pass_dict, result_fc_dict


async def download_all_medals():
    async with aiohttp.ClientSession() as session:
        async with session.get(
            OSEKAI_MEDALS_API, timeout=aiohttp.ClientTimeout(total=60)
        ) as response:
            response.raise_for_status()
            response_text = await response.text()

    match = re.search(r"const\s+medals_preload\s*=\s*(\{[\s\S]*?\});", response_text)
    if not match:
        raise ValueError("Osekai medals 页面中没有找到 medals_preload")
    payload = json.loads(match.group(1))

    medalstruct = payload.get("content")
    if not isinstance(medalstruct, list):
        raise ValueError("Osekai medals API 返回的数据中没有 content 列表")

    db_medal.drop()
    if medalstruct:
        db_medal.insert_many(medalstruct)

    medals_urls = []
    medals_ids = []

    for medal in medalstruct:
        link = medal["Link"]
        if not link.startswith(("http://", "https://")):
            link = f"{OSEKAI_MEDAL_ASSET_BASE_URL}/{link}"
        medals_urls.append(link)
        medals_ids.append(medal["Medal_ID"])

    await download_medal_async(medals_urls, medals_ids)

    return f"updated {len(medalstruct)} medals"
