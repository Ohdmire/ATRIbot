from bs4 import BeautifulSoup
from pathlib import Path
import os
import logging
from PIL import Image, ImageSequence
import io
from playwright.async_api import async_playwright
from ATRIlib.TOOLS.Download import download_resource_async
from ATRIlib.TOOLS.CommonTools import get_base64_encoded_data
import hashlib
from urllib.parse import urlparse
import shutil
import asyncio

Image.MAX_IMAGE_PIXELS = None

logger = logging.getLogger(__name__)

profile_result_path = Path('./data/tmp/profile')
ERROR_IMAGE_PATH = Path('./assets/error/error-404.png')

def extract_last_frame_from_gif(gif_content):
    """从GIF内容中提取最后一帧"""
    with Image.open(io.BytesIO(gif_content)) as img:
        # 如果不是GIF,直接返回原图
        if not getattr(img, "is_animated", False):
            return gif_content
        
        # 获取最后一帧
        last_frame = None
        for frame in ImageSequence.Iterator(img):
            last_frame = frame.copy()
        
        # 将最后一帧转换为bytes
        output = io.BytesIO()
        last_frame.save(output, format='PNG')
        return output.getvalue()

async def process_html(html_string):
    """
    处理HTML，下载资源并更新链接为相对路径
    """
    soup = BeautifulSoup(html_string, 'html.parser')
    resources_to_download = []

    # 确保资源目录存在
    resource_dir = profile_result_path / 'resources'
    resource_dir.mkdir(parents=True, exist_ok=True)

    # 复制错误图片到资源目录
    error_image_dest = resource_dir / 'error-404.png'
    shutil.copy(ERROR_IMAGE_PATH, error_image_dest)

    # 收集所有需要下载的资源
    for tag in soup.find_all(['img', 'link', 'script', 'svg']):
        if tag.name in ['img', 'svg']:
            src = tag.get('src') or tag.get('data')
            if src and src.startswith(('http://', 'https://')):
                resources_to_download.append((src, tag, 'src' if tag.name == 'img' else 'data'))
        elif tag.name == 'link' and tag.get('rel') == ['stylesheet']:
            href = tag.get('href')
            if href and href.startswith(('http://', 'https://')):
                resources_to_download.append((href, tag, 'href'))
        elif tag.name == 'script' and tag.get('src'):
            src = tag.get('src')
            if src and src.startswith(('http://', 'https://')):
                resources_to_download.append((src, tag, 'src'))

    # 处理 proportional-container
    for span in soup.find_all('span', class_='proportional-container'):
        if 'data-src' in span.attrs:
            del span['data-src']

    results = await download_resource_async(resources_to_download)

    # 更新HTML的链接
    for (url, tag, attr), (_, content, file_type) in zip(resources_to_download, results):
        if content:
            logger.info(f"处理资源: {url}, 文件类型: {file_type}")

            if file_type == 'svg':
                # SVG 处理
                try:
                    svg_content = content.decode('utf-8')
                    svg_soup = BeautifulSoup(svg_content, 'html.parser')
                    svg_tag = svg_soup.find('svg')
                    if svg_tag:
                        # 保存原始 img 标签的属性
                        original_attrs = dict(tag.attrs)
                        # 将原来的 img 标签替换为 svg 标签
                        tag.name = 'svg'
                        # 合并原始属性和 SVG 属性，保留 img 的样式
                        tag.attrs.update(svg_tag.attrs)
                        # 确保保留原始的 class 和 style 属性
                        for attr in ['class', 'style']:
                            if attr in original_attrs:
                                tag[attr] = original_attrs[attr]
                        # 添加 SVG 内容
                        tag.clear()
                        tag.extend(svg_tag.contents)
                        logger.info(f"IMG替换SVG保留样式: {tag}")
                    else:
                        logger.warning(f"SVG内容中未找到SVG标签: {url}")
                        tag[attr] = url  # 保留原始URL
                except Exception as e:
                    logger.error(f"处理SVG时出错: {str(e)}")
                    # 如果处理失败，保留原始URL
                    logger.info(f"保留原始SVG URL: {url}")
                    tag[attr] = url
            elif file_type == 'gif':
                # GIF 处理
                content = extract_last_frame_from_gif(content)
                file_ext = '.png'
                filename = hashlib.md5(url.encode()).hexdigest() + file_ext
                local_path = resource_dir / filename
                
                with open(local_path, 'wb') as f:
                    f.write(content)
                
                tag[attr] = f"resources/{filename}"
                logger.info(f"更新链接: {url} -> resources/{filename} (GIF转换为PNG)")
            else:
                # 其他资源的处理
                file_ext = os.path.splitext(urlparse(url).path)[1].lower() or '.bin'
                filename = hashlib.md5(url.encode()).hexdigest() + file_ext
                local_path = resource_dir / filename
                
                with open(local_path, 'wb') as f:
                    f.write(content)
                
                tag[attr] = f"resources/{filename}"
                logger.info(f"更新链接: {url} -> resources/{filename}")
        else:
            logger.warning(f"无法下载: {url}")
            if tag.name == 'img':
                tag[attr] = "resources/error-404.png"

    # # 清空所有 class="imagemap__link" 的 href 属性
    # for link in soup.find_all('a', class_='imagemap__link'):
    #     if 'href' in link.attrs:
    #         del link['href']

    # 清空所有 href 以 https://osu.ppy.sh/users/ 开头的链接
    for link in soup.find_all('a', href=lambda href: href and href.startswith('https://')):
        logger.info(f"清空链接: {link}")
        del link['href']

    return str(soup)

async def html_to_image(html_string, max_body_width=1650, avatar_url=None, username=None, user_id=None):
    """
    将HTML字符串渲染成图片，写入文件，然后返回BytesIO对象
    """
    # 简单处理HTML，不下载外部资源
    html_string = await process_html(html_string)

    # 添加头像和用户名
    avatar_html = ""
    if avatar_url:
        avatar_html = f'''
        <div style="display: flex; justify-content: center; align-items: center; margin-bottom: 20px;">
            <img src="{avatar_url}" style="width: 200px; height: 200px; border-radius: 50%;">
        </div>
        '''
    username_html = f'<div style="text-align: center; margin-bottom: 20px; color: white;"><strong>{username}</strong></div>' if username else ""
    
    # 添加分割线
    divider_html = '<hr style="border: 0; height: 1px; background: #ffffff; margin: 20px 0;">'

    # 添加CSS样式
    css = f"""
    <style>
        body {{
            font-family: 'CustomFont', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol";
            font-size: 36px;
            max-width: {max_body_width}px;
            margin: 0 auto;
            padding: 20px;
            box-sizing: border-box;
            color: white;
            background-color: #5c6570;
        }}
        h1 {{ font-size: 32px; }}
        h2 {{ font-size: 28px; }}
        p {{ font-size: 20px; }}

        .bbcode-spoilerbox__link {{
            text-align: left;
            display: flex;
            align-items: center;
            flex-wrap: wrap;
            overflow-wrap: anywhere;
            font-weight: bold;
            width: max-content;
            max-width: 100%;
            color: #66ccff;  /* 新的颜色：浅蓝色 */
            text-decoration: none;  /* 移除下划线 */
        }}

        .bbcode-spoilerbox__link::before {{
            content: "↴";  /* 开头添加向下箭头 */
            display: inline-block;
            margin-right: 5px;
            font-size: 1.2em;  /* 微增大箭头大小 */
            line-height: 1;  /* 确保箭头垂直对齐 */
        }}

        /* 新添加规则：将 rel="nofollow" 的链接颜色改为浅绿色 */
        a[rel="nofollow"] {{
            color: #90EE90;  /* 浅绿色 */
        }}

        /* Wells */
        .well {{
            min-height: 20px;
            padding: 19px;
            margin-bottom: 20px;
            background-color: #394146;  /* 更改为新的背景颜色 */
            border: 1px solid #4a5258;  /* 稍微调亮的边框颜色 */
            border-radius: 4px;
            box-shadow: inset 0 1px 1px rgba(0, 0, 0, .05);
            color: #ffffff;  /* 确保文字在色背景上可见 */
            text-align: left;  /* 添加这行来保持well内容左对齐 */
        }}
        .well blockquote {{
            border-color: #4a5258;
            border-color: rgba(255, 255, 255, 0.15);
        }}
        .well-lg {{
            padding: 24px;
            border-radius: 6px;
        }}
        .well-sm {{
            padding: 9px;
            border-radius: 3px;
        }}

        /* 新添加的 .proportional-container 相关样式 */
        .proportional-container {{
            max-width: 100%;
            display: inline-block;
            vertical-align: top;
        }}

        .proportional-container__height {{
            display: block;
            position: relative;
            max-width: {max_body_width}px;
            margin: 0 auto;
            overflow: hidden;  /* 添加这行，防止内容溢出 */
        }}

        .proportional-container__content {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            max-width: 100%;  /* 修改这行 */
            max-height: 100%;  /* 修改这行 */
            object-fit: contain;
        }}

        .proportional-container img,
        .proportional-container svg {{
            max-width: 100%;
            max-height: 100%;
            width: auto;
            height: auto;
            object-fit: contain;
        }}

        /* 添加 .bbcode-spoilerbox__body 的样式 */
        .bbcode-spoilerbox__body {{
            margin-left: 20px;  /* 左侧偏移 */
            padding: 10px;  /* 内边距 */
            border-left: 2px solid #66ccff;  /* 左侧边框，使用浅蓝色 */
            margin-top: 5px;  /* 与标题的间距 */
        }}
    </style>
    """
    
    # 修改 js 变量中的 JavaScript 代码

    js = """
    <script>
document.addEventListener('DOMContentLoaded', function() {
    // 处理所有图片和SVG
    var images = document.querySelectorAll('img, svg');
    images.forEach(function(img) {
        var parent = img.parentElement;
        if (parent) {
            parent.style.textAlign = 'center';
            img.style.maxWidth = '100%';
            img.style.maxHeight = '100%';
            img.style.width = 'auto';
            img.style.height = 'auto';
            img.style.objectFit = 'contain';
        }
    });

    // 特别处理 proportional-container
    var proportionalContainers = document.querySelectorAll('.proportional-container');
    proportionalContainers.forEach(function(container) {
        var content = container.querySelector('.proportional-container__content');
        if (content) {
            var img = content.querySelector('img, svg');
            if (img) {
                img.style.maxWidth = '100%';
                img.style.maxHeight = '100%';
                img.style.width = 'auto';
                img.style.height = 'auto';
                img.style.objectFit = 'contain';
            }
        }
    });

    // 确保文字段落保持左对齐
    var paragraphs = document.querySelectorAll('p');
    paragraphs.forEach(function(p) {
        p.style.textAlign = 'left';
    });
});
</script>
    """
    
    # 将CSS、JavaScript、头像、用户名和分割线插入到HTML内容中，并添加<html>标签
    html_with_css = f"<html><head>{css}{js}</head><body>{avatar_html}{username_html}{divider_html}{html_string}</body></html>"
    
    # 将HTML内容写入临时文件
    temp_html_path = profile_result_path / f"{user_id}_temp.html"
    with open(temp_html_path, 'w', encoding='utf-8') as f:
        f.write(html_with_css)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context(viewport={'width': max_body_width, 'height': 1080})
        page = await context.new_page()
        await page.goto(f"file://{temp_html_path.absolute()}")

        # 等待所有图片加载完成，设置超时时间为10秒
        try:
            await page.evaluate("""
                () => Promise.race([
                    Promise.all(
                        Array.from(document.images)
                            .filter(img => !img.complete)
                            .map(img => new Promise((resolve, reject) => {
                                img.onload = resolve;
                                img.onerror = reject;
                            }))
                    ),
                    new Promise((_, reject) => setTimeout(() => reject(new Error('Image loading timeout')), 10000))
                ])
            """)
        except Exception as e:
            logger.warning(f"图片加载超时或发生错误: {str(e)}")

        # 获取页面高度
        page_height = await page.evaluate("""
            () => Math.max(
                document.body.scrollHeight,
                document.body.offsetHeight,
                document.documentElement.clientHeight,
                document.documentElement.scrollHeight,
                document.documentElement.offsetHeight
            )
        """)

        # 网页等待1s
        await asyncio.sleep(1)

        # 如果页面高度超过32768，分成两部分截图
        if page_height > 32768:
            first_part_height = 32768
            second_part_height = page_height - 32768

            # 截取第一部分
            await page.set_viewport_size({"width": max_body_width, "height": first_part_height})
            first_part_path = profile_result_path / f"{user_id}_part1.png"
            await page.screenshot(path=str(first_part_path), full_page=False, clip={"x": 0, "y": 0, "width": max_body_width, "height": first_part_height})

            # 滚动到第二部分
            await page.evaluate(f"window.scrollTo(0, {first_part_height})")
            
            # 等待一段时间让页面稳定
            await asyncio.sleep(2)

            # 等待可能的动态内容加载
            try:
                await page.wait_for_function("""
                    () => {
                        const images = Array.from(document.images);
                        return images.every(img => img.complete);
                    }
                """, timeout=10000)
            except Exception as e:
                logger.warning(f"等待图片part2加载完成时发生错误: {str(e)}")

            # 截取第二部分
            await page.set_viewport_size({"width": max_body_width, "height": second_part_height})
            second_part_path = profile_result_path / f"{user_id}_part2.png"
            await page.screenshot(path=str(second_part_path), full_page=False, clip={"x": 0, "y": 0, "width": max_body_width, "height": second_part_height})

            # 合并两部分图片
            with Image.open(first_part_path) as img1, Image.open(second_part_path) as img2:
                total_height = img1.height + img2.height
                max_allowed_height = 24000
                
                if total_height > max_allowed_height:
                    # 计算缩放比例
                    scale_factor = max_allowed_height / total_height
                    new_width = int(max_body_width * scale_factor)
                    new_height1 = int(img1.height * scale_factor)
                    new_height2 = int(img2.height * scale_factor)
                    
                    img1 = img1.resize((new_width, new_height1), Image.LANCZOS)
                    img2 = img2.resize((new_width, new_height2), Image.LANCZOS)
                
                # 创建新图像并粘贴两部分
                combined_img = Image.new('RGB', (img1.width, img1.height + img2.height))
                combined_img.paste(img1, (0, 0))
                combined_img.paste(img2, (0, img1.height))
                
                # 保存为JPEG
                jpeg_output_path = profile_result_path / f"{user_id}.jpg"
                combined_img.save(jpeg_output_path, 'JPEG', quality=95, optimize=True)
            
            # 清理临时文件
            # os.remove(first_part_path)
            # os.remove(second_part_path)
        else:
            # 如果页面高度不超过32768，直接截图
            await page.set_viewport_size({"width": max_body_width, "height": page_height})
            png_output_path = profile_result_path / f"{user_id}.png"
            await page.screenshot(path=str(png_output_path), full_page=True)
            
            # 转换为JPEG
            with Image.open(png_output_path) as img:
                if img.height > 24000:
                    # 缩放图片
                    scale_factor = 24000 / img.height
                    new_size = (int(img.width * scale_factor), 24000)
                    img = img.resize(new_size, Image.LANCZOS)
                
                jpeg_output_path = profile_result_path / f"{user_id}.jpg"
                img.convert('RGB').save(jpeg_output_path, 'JPEG', quality=95, optimize=True)
            
            # 清理临时文件
            os.remove(png_output_path)

        await browser.close()

    # 读取生成的JPEG文件
    with open(jpeg_output_path, 'rb') as f:
        img_byte_arr = io.BytesIO(f.read())

    # 清理临时文件
    # os.remove(jpeg_output_path)
    # os.remove(temp_html_path)
    # for file in (profile_result_path / 'resources').glob('*'):
    #     os.remove(file)

    img_byte_arr.seek(0)
    return img_byte_arr

async def draw_profile(html_content, avatar_url, username, user_id):
    result = await html_to_image(html_content, max_body_width=1650, avatar_url=avatar_url, username=username, user_id=user_id)
    return result
