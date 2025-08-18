import asyncio
import logging
import io

from ATRIlib.API.PPYapiv2 import get_changelog_list,get_lazer_changelog,get_stable_changelog,get_tachyon_changelog
import markdown
from ATRIlib.Config import path_config

import aiofiles
from collections import defaultdict
from ATRIlib.API.deepseek import batch_translate

from ATRIlib.DRAW.draw_changelog import html_to_image

changelog_result_path = path_config.changelog_result_path

async def format_changelog_entries_markdown(changelog_entries):
    # 首先按category分组，但保持原始顺序
    category_groups = defaultdict(list)
    # 同时保留所有条目的原始顺序
    all_entries_in_order = []

    for entry in changelog_entries:
        category_groups[entry["category"]].append(entry)
        all_entries_in_order.append(entry)

    # 收集所有需要翻译的文本（按照原始顺序）
    all_titles = []
    all_messages = []
    message_indices = []  # 记录哪些条目有message需要翻译

    for idx, entry in enumerate(all_entries_in_order):
        all_titles.append(entry["title"])
        if entry.get("message"):  # 只有message存在且非空时才加入翻译
            all_messages.append(entry["message"])
            message_indices.append(idx)

    # 批量翻译（保持原始顺序）
    translated_titles = await batch_translate(all_titles)
    # 只翻译有message的条目
    translated_messages_list = await batch_translate(all_messages) if all_messages else []

    # 创建翻译结果映射表（按原始顺序）
    translation_map = {}
    for idx, entry in enumerate(all_entries_in_order):
        # 初始化翻译结果
        trans_data = {
            "title": translated_titles[idx],
            "message": ""  # 默认空消息
        }

        # 如果这个条目在message_indices中，说明它有message需要翻译
        if idx in message_indices:
            # 找到它在translated_messages_list中的位置
            msg_idx = message_indices.index(idx)
            trans_data["message"] = translated_messages_list[msg_idx]

        translation_map[id(entry)] = trans_data

    # 重建翻译后的条目（按分类排序）
    raw_md = ""
    for category in sorted(category_groups.keys(), key=lambda x: x.lower()):
        entries = category_groups[category]
        raw_md += f"## {category}\n\n"

        for entry in entries:
            # 从映射表中获取翻译结果
            trans = translation_map[id(entry)]
            title_trans = trans["title"]
            message_trans = trans["message"]

            # 添加类型前缀
            prefix = "+ " if entry["type"] == "add" else ""

            # 处理major条目
            original_title = entry["title"]
            if entry["major"]:
                title_display = f"<span style='color: #f2c000; font-weight: bold'>{title_trans}</span>"
            else:
                title_display = f"<span style='color: #ffffff; font-weight: bold'>{title_trans}</span>"

            # 构建条目内容
            raw_md += f"### {prefix}{title_display}"
            raw_md += f'<br/>'
            if entry["major"]:
                raw_md += f"<div style='font-size: 0.8em; color: #998848'>{original_title}</div>\n\n"
            else:
                raw_md += f"<div style='font-size: 0.8em; color: #aaaaaa'>{original_title}</div>\n\n"

            # 添加消息内容（只有有message时才添加）
            if entry.get("message"):
                raw_md += f"<div style='margin-left: 20px;'>{message_trans}</div>"
                # raw_md += f'<br/>'
                raw_md += f"<div style='font-size: 0.8em; color: #aaaaaa; margin-left: 20px;'>{entry['message']}</div>\n\n"

    html_raw = markdown.markdown(raw_md, extensions=['extra'])
    return html_raw

async def get_changelog_status(stream_name):

    stream_name = stream_name.strip().lower()

    stream_handlers = {
        "stable": get_stable_changelog,
        "lazer": get_lazer_changelog,
        "tachyon": get_tachyon_changelog
    }

    result = await stream_handlers.get(stream_name, get_lazer_changelog)()
    return result

async def calculate_changelog_draw(stream_name,index,cache):

    result = await get_changelog_status(stream_name)

    builds = result['builds']

    version = f"{builds[index - 1]['update_stream']['name']}-{builds[index - 1]['display_version']}"

    # 判断是否已经有渲染过的文件有则直接返回
    cache_file = changelog_result_path / f"{version}.jpg"
    if cache_file.exists() and cache:
        async with aiofiles.open(cache_file, "rb") as f:
            logging.info(f"返回changelog缓存: {cache_file}")
            img_data = await f.read()
            # 转换为BytesIO并记录大小
            img_byte_arr = io.BytesIO(img_data)
            img_byte_arr.seek(0)

            image_size = img_byte_arr.getbuffer().nbytes
            logging.info(f"图片大小: {image_size / 1024 / 1024:.2f} MB")

            return img_byte_arr
    else:
        html_result = await format_changelog_entries_markdown(builds[index - 1]['changelog_entries'])
        result = await html_to_image(version, html_result)
        return result




