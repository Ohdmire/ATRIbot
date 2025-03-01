from ATRIlib.API.github import get_news_url,replace_github_domain_own
from ATRIlib.API.deepseek import translate
from ATRIlib.TOOLS.Download import download_news_markdown,news_path
from ATRIlib.DRAW.draw_news import draw_news
import re

def format_markdown(content):
    # 提取 title 和 date
    title = content.split('title: ')[1].split('\n')[0]
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

def add_gh_proxy(content):
    # 使用正则表达式替换所有匹配的字段
    pattern = r'https://raw\.githubusercontent\.com'
    replacement = r'https://gh-proxy.com/https://raw.githubusercontent.com'
    return re.sub(pattern, replacement, content)



async def calculate_news(index):
    url,markdown_name = await get_news_url(index)

    # 判断是否存在文件

    translated_filepath = news_path / (markdown_name + "_translated.md")
    raw_filepath = news_path / (markdown_name + ".md")

    if translated_filepath.exists():
        with open(translated_filepath,"r") as f:
            translated_content = f.read()
    else:
        # 下载文件
        await download_news_markdown(markdown_name, url)
        with open(raw_filepath,"r") as f:
            raw = f.read()
            raw = format_markdown(raw)
            raw = complete_url_in_markdown(raw)
            raw = add_gh_proxy(raw)
            translated_content = translate(raw)
            # translated_content = raw
            with open(translated_filepath,"w") as f:
                f.write(translated_content)

    result = await draw_news(markdown_name,translated_content)

    return result







