import aiohttp
import asyncio
from PIL import Image
from io import BytesIO
import logging
import mimetypes
from ATRIlib.Config import path_config

beatmaps_path = path_config.beatmaps_path
beatmaps_path_tmp = path_config.beatmaps_path_tmp
avatar_path = path_config.avatar_path
cover_path = path_config.cover_path
medal_path = path_config.medal_path
news_path = path_config.news_path

semaphore = asyncio.Semaphore(16)
semaphore_small = asyncio.Semaphore(4)
PROFILE_IMAGE_BACKGROUND = (92, 101, 112)
OSU_WEB_BASE_URL = "https://osu.ppy.sh"
OSU_WEB_USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:150.0) Gecko/20100101 Firefox/150.0"


def compress_image_to_jpeg(content, background_color=PROFILE_IMAGE_BACKGROUND):
    with Image.open(BytesIO(content)) as img:
        if getattr(img, "is_animated", False):
            # Animated images, including GIF, are flattened to their last frame.
            last_frame = None
            for frame in range(img.n_frames):
                img.seek(frame)
                last_frame = img.copy()
            img = last_frame
        else:
            img = img.copy()

    has_alpha = img.mode in ("RGBA", "LA") or (
        img.mode == "P" and "transparency" in img.info
    )
    if has_alpha:
        rgba = img.convert("RGBA")
        background = Image.new("RGBA", rgba.size, background_color + (255,))
        background.alpha_composite(rgba)
        img = background.convert("RGB")
    elif img.mode != "RGB":
        img = img.convert("RGB")

    img_io = BytesIO()
    img.save(img_io, format='JPEG', quality=95, optimize=True)
    return img_io.getvalue()


# 下载ppy的资源(图片)
async def download_resource(session, url):
    """
    异步下载资源并保存到内存中，对图片进行压缩，并返回文件类型
    """
    try:
        async with semaphore_small:
            async with session.get(url, timeout=5) as response:
                if response.status == 200:
                    content_type = response.headers.get('Content-Type', '')
                    content = await response.read()
                    
                    # 检查是否为SVG文件
                    mime_type, _ = mimetypes.guess_type(url)
                    if mime_type == 'image/svg+xml' or content_type.startswith('image/svg+xml'):
                        logging.info(f"下载了SVG文件: {url}")
                        return url, content, 'svg'

                    # 如果是其他类型的图片，进行压缩
                    if content_type.startswith('image') or (
                        mime_type and mime_type.startswith('image/')
                    ):
                        content = compress_image_to_jpeg(content)
                        logging.info(f"下载资源 {url} 成功，压缩后大小为 {len(content)} 字节")
                        return url, content, 'image'
                    return url, content, 'other'
                else:
                    logging.error(f"下载{url}网络错误{response.status}")
    except Exception as e:
        logging.error(f"下载资源时出错: {url}, 错误: {type(e)} {str(e)}")
    return url, None, None
        
async def download_resource_async(resources_to_download):
    async with aiohttp.ClientSession() as session:
        tasks = [download_resource(session, url) for url, _, _ in resources_to_download]
        return await asyncio.gather(*tasks)


def normalize_osu_session_cookie(value):
    cookie = value.strip()
    if not cookie:
        return ""
    if cookie.startswith("osu_session=") or "; osu_session=" in cookie or ";osu_session=" in cookie:
        return cookie
    if cookie.startswith("Cookie:"):
        cookie = cookie.removeprefix("Cookie:").strip()
        if cookie.startswith("osu_session=") or "; osu_session=" in cookie or ";osu_session=" in cookie:
            return cookie
        return cookie
    return f"osu_session={cookie}"


async def download_replay_file_from_web(score_id, target_path, osu_session):
    if not osu_session:
        raise ValueError("OSU_TOKEN 未设置")
    url = f"{OSU_WEB_BASE_URL}/scores/{score_id}/download"
    headers = {
        "Accept": "application/octet-stream",
        "Cookie": normalize_osu_session_cookie(osu_session),
        "Referer": f"{OSU_WEB_BASE_URL}/scores/{score_id}",
        "User-Agent": OSU_WEB_USER_AGENT,
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=60)) as response:
            if response.status == 404:
                raise ValueError(f"score {score_id} 没有可下载 replay")
            if response.status >= 400:
                text = await response.text()
                raise ValueError(f"replay 下载失败: HTTP {response.status} {text[:120]}")
            content_type = response.headers.get("content-type", "")
            if "text/html" in content_type:
                raise ValueError(f"replay 下载返回 HTML，请检查 OSU_TOKEN 浏览器 cookie 是否有效: score {score_id}")
            content = await response.read()
    if not content:
        raise ValueError(f"score {score_id} replay 下载结果为空")
    target_path.parent.mkdir(parents=True, exist_ok=True)
    partial = target_path.with_suffix(target_path.suffix + ".part")
    partial.write_bytes(content)
    partial.replace(target_path)


async def download_replay_file_from_api(score_id, target_path, bearer_token):
    if not bearer_token:
        raise ValueError("API v2 token 不存在")
    url = f"{OSU_WEB_BASE_URL}/api/v2/scores/{score_id}/download"
    headers = {
        "Accept": "application/octet-stream",
        "Authorization": f"Bearer {bearer_token}",
        "x-api-version": "20240529",
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=60)) as response:
            if response.status == 404:
                raise ValueError(f"score {score_id} 没有可下载 replay")
            if response.status >= 400:
                text = await response.text()
                raise ValueError(f"API v2 replay 下载失败: HTTP {response.status} {text[:120]}")
            content_type = response.headers.get("content-type", "")
            if "text/html" in content_type:
                raise ValueError(f"API v2 replay 下载返回 HTML: score {score_id}")
            content = await response.read()
    if not content:
        raise ValueError(f"score {score_id} API v2 replay 下载结果为空")
    target_path.parent.mkdir(parents=True, exist_ok=True)
    partial = target_path.with_suffix(target_path.suffix + ".part")
    partial.write_bytes(content)
    partial.replace(target_path)


async def download_replay_file(score_id, target_path, osu_session, bearer_token=None):
    web_error = None
    try:
        await download_replay_file_from_web(score_id, target_path, osu_session)
        return "web"
    except Exception as e:
        web_error = e

    try:
        await download_replay_file_from_api(score_id, target_path, bearer_token)
        return "api_v2"
    except Exception as e:
        raise ValueError(f"replay 下载失败，web: {web_error}; api_v2: {e}")


# 下载谱面
async def download_beatmap_file(session, beatmap_id, Temp=True):
    if Temp:
        file_path = beatmaps_path_tmp / f'{beatmap_id}.osu'
    else:
        file_path = beatmaps_path / f'{beatmap_id}.osu'
    url = f'https://osu.ppy.sh/osu/{beatmap_id}'
    async with semaphore:
        async with session.get(url) as response:
            if response.status == 200:  # 检查状态码是否为200
                with open(file_path, 'wb') as file:
                    while True:
                        chunk = await response.content.read(1024)
                        if not chunk:
                            break
                        file.write(chunk)
            else:
                print(
                    f'Error: {response.status} {response.reason} - {url}')

# 下载头像
async def download_avatar_file(session, avatar_url, user_id):
    url = avatar_url
    async with semaphore:
        async with session.get(url) as response:
            if response.status == 200:  # 检查状态码是否为200
                avatar_file = avatar_path / f'{user_id}.jpeg'
                with open(avatar_file, 'wb') as file:
                    while True:
                        chunk = await response.content.read(1024)
                        if not chunk:
                            break
                        file.write(chunk)
            else:
                print(
                    f'Error: {response.status} {response.reason} - {url}')

# 下载封面
async def download_cover(cover_url, beatmapset_id):
    url = cover_url
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:  # 检查状态码是否为200
                cover_file = cover_path / f'{beatmapset_id}.jpg'
                with open(cover_file, 'wb') as file:
                    while True:
                        chunk = await response.content.read(1024)
                        if not chunk:
                            break
                        file.write(chunk)

# 下载奖牌
async def download_medal(session, medal_url, medalid):
    url = medal_url
    async with semaphore:
        async with session.get(url) as response:
            if response.status == 200:  # 检查状态码是否为200
                medal_file = medal_path / f'{medalid}.png'
                with open(medal_file, 'wb') as file:
                    while True:
                        chunk = await response.content.read(1024)
                        if not chunk:
                            break
                        file.write(chunk)
            else:
                print(
                    f'Error: {response.status} {response.reason} - {url}')

# 批量下载谱面
async def download_osu_async(beatmap_ids, Temp=True):
    async with aiohttp.ClientSession() as session:
        tasks = [download_beatmap_file(session, beatmap_id, Temp)
                 for beatmap_id in beatmap_ids]
        await asyncio.gather(*tasks)

# 批量下载头像
async def download_avatar_async(avatar_urls, user_ids):
    async with aiohttp.ClientSession() as session:
        tasks = [download_avatar_file(session, avatar_url, user_id)
                 for avatar_url, user_id in zip(avatar_urls, user_ids)]
        await asyncio.gather(*tasks)

# 批量下载奖章
async def download_medal_async(medal_urls, medal_ids):
    async with aiohttp.ClientSession() as session:
        tasks = [download_medal(session, medal_url, medal_id)
                 for medal_url, medal_id in zip(medal_urls, medal_ids)]
        await asyncio.gather(*tasks)


# 获取单个谱面(ranked or unranked)
async def fetch_beatmap_file_async_one(beatmap_id, Temp=True):
    if Temp:
        filepath = beatmaps_path_tmp / f'{beatmap_id}.osu'
    else:
        filepath = beatmaps_path / f'{beatmap_id}.osu'
    if filepath.exists():
        return
    else:
        beatmap_ids = [beatmap_id]
    await download_osu_async(beatmap_ids, Temp=Temp)


# 批量获取谱面(ranked or unranked)
async def fetch_beatmap_file_async_all(beatmap_id_list, Temp=False):
    beatmap_ids = []
    for beatmap_id in beatmap_id_list:
        file_path = beatmaps_path / f'{beatmap_id}.osu'
        if file_path.exists():
            pass
        else:
            beatmap_ids.append(beatmap_id)

    await download_osu_async(beatmap_ids, Temp=Temp)

# 获取新闻
async def download_news_markdown(title, url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:  # 检查状态码是否为200
                markdown_file = news_path / f'{title}.md'
                with open(markdown_file, 'wb') as file:
                    async for chunk in response.content.iter_chunked(1024):
                        file.write(chunk)
            else:
                print(f'Error: {response.status} {response.reason} - {url}')
