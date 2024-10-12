from ATRIlib.TOOLS.Download import download_resource_async
from ATRIlib.TOOLS.CommonTools import get_base64_encoded_data
import imgkit
from bs4 import BeautifulSoup
import mimetypes
from io import BytesIO
from pathlib import Path
import os
import logging
import subprocess
from PIL import Image
import io

Image.MAX_IMAGE_PIXELS = None

logger = logging.getLogger(__name__)

profile_result_path = Path('./data/tmp/profile')

default_image_path = Path('./assets/error')


# 添加默认错误图片的路径
ERROR_IMAGE_PATH = Path('./assets/error/error-404.png')

async def process_html(html_string):
    """
    处理HTML，异步下载外部资源并更新链接
    """
    soup = BeautifulSoup(html_string, 'html.parser')
    resources_to_download = []

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

    results = await download_resource_async(resources_to_download)

    # 预先加载错误图片的 base64 编码
    with open(ERROR_IMAGE_PATH, 'rb') as f:
        error_image_content = f.read()
    error_image_base64 = get_base64_encoded_data(error_image_content, 'image/png')

    # 更新HTML中的链接
    for (url, tag, attr), (_, content) in zip(resources_to_download, results):
        if content:
            mime_type, _ = mimetypes.guess_type(url)
            if mime_type == 'image/svg+xml':
                # 对于SVG，我们直接将内容嵌入到HTML中
                svg_content = content.decode('utf-8')
                new_tag = soup.new_tag('svg')
                new_tag.append(BeautifulSoup(svg_content, 'html.parser'))
                tag.replace_with(new_tag)
            else:
                base64_data = get_base64_encoded_data(content, mime_type)
                tag[attr] = base64_data
            logger.warning(f"更新链接: {url}")
        else:
            logger.warning(f"无法下载: {url}")
            if tag.name == 'img':
                tag[attr] = error_image_base64
            elif tag.name == 'svg':
                tag.decompose()  # 如果无法下载SVG，则移除该标签
                
    return str(soup)

async def html_to_image(html_string, max_img_width=1400, max_img_height=800, max_body_width=1650, avatar_url=None, username=None,user_id=None):
    """
    将HTML字符串渲染成图片，写入文件，然后返回BytesIO对象
    :param html_string: HTML内容
    :param max_img_width: 图片最大宽度(像素)
    :param max_img_height: 图片最大高度(像素)
    :param max_body_width: 整体内容最大宽度(像素)
    :param avatar_url: 头像的URL
    :param username: 用户名
    :return: BytesIO对象，包含生成的图片数据
    """
    # 处理外部资源
    html_string = await process_html(html_string)

    # 添加头像和用户
    avatar_html = ""
    if avatar_url:
        avatar_html = f'<div style="text-align: center;"><img src="{avatar_url}" style="width: 200px; height: 200px; border-radius: 50%; margin-bottom: 10px;"></div>'
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
        img {{
            max-width: {max_img_width}px;
            width: auto;
            height: auto;
            display: block;
            margin: 20px auto;
        }}

        /* 修改后的 CSS */
        .bbcode-spoilerbox {{
            --link-icon: '\f107';  /* fa-angle-down */
        }}

        .bbcode-spoilerbox__body {{
            display: block;  /* 保持原有的块级显示 */
            margin-top: 10px;
            padding-left: 40px;
        }}

        .bbcode-spoilerbox__body img {{
            max-width: calc(50% - 10px);  /* 两列布局，留出间隔 */
            width: auto;
            height: auto;
            display: inline-block;  /* 允许图片并排显示 */
            vertical-align: top;  /* 顶部对齐 */
            margin: 0 5px 20px;  /* 左右间隔5px，底部间隔20px */
        }}

        @media (max-width: 800px) {{
            .bbcode-spoilerbox__body img {{
                max-width: 100%;  /* 在较窄的屏幕上切换到单列 */
                margin-left: 0;
                margin-right: 0;
            }}
        }}

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
            content: "↴";  /* 在开头添加向下箭头 */
            display: inline-block;
            margin-right: 5px;
            font-size: 1.2em;  /* 稍微增大箭头大小 */
            line-height: 1;  /* 确保箭头垂直对齐 */
        }}

        /* 新添加的规则：将 rel="nofollow" 的链接颜色改为浅绿色 */
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
            color: #ffffff;  /* 确保文字在深色背景上可见 */
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
    </style>
    """
    
    # 添加JavaScript来展开所有spoiler
    js = """
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        var spoilers = document.querySelectorAll('.bbcode-spoilerbox');
        spoilers.forEach(function(spoiler) {
            spoiler.classList.add('js-spoilerbox--open');
        });
    });
    </script>
    """
    
    # 将CSS、JavaScript、头像、用户名和分割线插入到HTML内容中，并添加<html>标签
    html_with_css = f"<html><head>{css}{js}</head><body>{avatar_html}{username_html}{divider_html}{html_string}</body></html>"
    
    options = {
        'format': 'svg',
        'encoding': "UTF-8",
        'quality': 100,
        'width': max_body_width + 50,  # 加一些额外的宽度以适应内边距
    }
    svg_output_path = f"{profile_result_path}/{user_id}.svg"
    png_output_path = f"{profile_result_path}/{user_id}.png"
    try:
        imgkit.from_string(html_with_css, svg_output_path, options=options)
    except Exception as e:
        logger.warning(f"生成图片失败: {str(e)}")
        
    # 记录生成的SVG文件大小
    svg_file_size = os.path.getsize(svg_output_path)
    logger.info(f"生成的SVG文件大小: {svg_file_size / 1024 / 1024:.2f} MB")

    # 使用Inkscape将SVG转换为PNG
    inkscape_command = [
        "inkscape",
        "--export-type=png",
        f"--export-filename={png_output_path}",
        svg_output_path
    ]
    subprocess.run(inkscape_command, check=True)

    # 压缩PNG文件并转换为JPEG
    with Image.open(png_output_path) as img:
        # 确保图片尺寸不超过65000x65000
        max_size = 24000
        if img.width > max_size or img.height > max_size:
            ratio = min(max_size / img.width, max_size / img.height)
            new_size = (int(img.width * ratio), int(img.height * ratio))
            img = img.resize(new_size, Image.LANCZOS)

        # 转换图像模式为RGB
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')

        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG', quality=95, optimize=True)
        
        img_size = len(img_byte_arr.getvalue())
        logger.info(f"压缩后的JPEG文件大小: {img_size / 1024 / 1024:.2f} MB，质量: 95%")

    # 清理临时文件
    os.remove(svg_output_path)
    os.remove(png_output_path)

    img_byte_arr.seek(0)
    return img_byte_arr

async def draw_profile(html_content, avatar_url, username,user_id):
    result = await html_to_image(html_content, max_img_width=1400, max_img_height=800, max_body_width=1650, avatar_url=avatar_url, username=username,user_id=user_id)
    return result
