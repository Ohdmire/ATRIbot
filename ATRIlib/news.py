import asyncio
import re

from ATRIlib.API.deepseek import translate
from ATRIlib.API.PPYapiv2 import get_news_list, get_news_post
from ATRIlib.Config import path_config
from ATRIlib.DRAW.draw_news import draw_news

news_path = path_config.news_path

NEWS_PAGE_LIMIT = 21


def format_markdown(content):
    # 提取 title 和 date
    title = content.split('title: ')[1].split('\n')[0].strip().strip('"').strip("'")
    date = content.split('date: ')[1].split(' +')[0]

    # 转换为 Markdown 格式
    markdown_title = f"# {title}"
    markdown_date = f"{date}"

    if content.startswith('---'):
        content = content.split('---', 2)[2].strip()

    result = markdown_title + '\n' + markdown_date + '\n' + "---" + '\n' + content

    return result


def complete_url_in_markdown(content):
    # 使用正则表达式替换所有匹配的字段
    pattern = r'!\[\]\(/wiki'
    replacement = r'![](https://raw.githubusercontent.com/ppy/osu-wiki/master/wiki'
    return re.sub(pattern, replacement, content)


async def get_news_content(index):
    index = max(1, int(index or 1))
    collected = []
    cursor_string = None

    while len(collected) < index:
        params = {"limit": NEWS_PAGE_LIMIT}
        if cursor_string:
            params["cursor_string"] = cursor_string

        data = await get_news_list(params)
        if "error" in data:
            raise ValueError(data["error"])

        posts = data.get("news_posts", [])
        if not posts:
            break

        collected.extend(posts)
        cursor_string = data.get("cursor_string")
        if not cursor_string:
            break

    if not collected:
        raise ValueError("没有找到新闻")

    post = collected[min(index, len(collected)) - 1]
    detail = await get_news_post(post["slug"])
    if "error" in detail:
        raise ValueError(detail["error"])

    content = detail.get("content_markdown") or ""
    if not content:
        raise ValueError("无法获取新闻内容")

    return content, detail.get("slug") or post["slug"]


async def calculate_news(index, is_raw_news=False):
    raw_content, markdown_name = await get_news_content(index)

    raw = format_markdown(raw_content)
    raw = complete_url_in_markdown(raw)

    translated_filepath = news_path / (markdown_name + "_translated.md")
    raw_filepath = news_path / (markdown_name + ".md")

    news_path.mkdir(parents=True, exist_ok=True)
    with open(raw_filepath, "w", encoding="utf-8") as f:
        f.write(raw)

    if is_raw_news:
        return await draw_news(markdown_name, raw)

    if translated_filepath.exists():
        with open(translated_filepath, "r", encoding="utf-8") as f:
            translated_content = f.read()
    else:
        translated_content = await asyncio.to_thread(translate, raw)
        if not translated_content:
            translated_content = raw
        with open(translated_filepath, "w", encoding="utf-8") as f:
            f.write(translated_content)

    return await draw_news(markdown_name, translated_content)
