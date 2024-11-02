from PIL import Image, ImageDraw, ImageFont
import io
from pathlib import Path
import textwrap
import re

def parse_diff(diff_text):
    """解析差异文本，返回删除行和添加行"""
    # 解析 @@ 行来获取行号信息
    header_match = re.match(r'@@ -(\d+),(\d+) \+(\d+),(\d+) @@', diff_text.split('\n')[0])
    if not header_match:
        return None
    
    lines = diff_text.split('\n')[1:]  # 跳过 @@ 行
    return lines

def draw_commit(diff_text, width=1000, line_height=30, padding=20):
    """
    绘制 GitHub 风格的 commit 差异图
    
    参数:
        diff_text: 包含差异信息的文本
        width: 图片宽度
        line_height: 每行高度
        padding: 内边距
    """
    # 设置字体
    try:
        font = ImageFont.truetype("NotoSansMono-Regular.ttf", 16)
    except:
        try:
            font = ImageFont.truetype("Noto Sans Mono Regular", 16)
        except:
            try:
                font = ImageFont.truetype("Noto Sans Mono", 16)
            except:
                font = ImageFont.load_default()

    # 解析差异文本
    lines = parse_diff(diff_text)
    if not lines:
        return None

    # 计算最长行的宽度
    max_width = 0
    header_line = diff_text.split('\n')[0]
    header_width = font.getlength(header_line) + 2 * padding
    max_width = max(max_width, header_width)
    
    for line in lines:
        if line:
            line_width = font.getlength(line) + 2 * padding
            max_width = max(max_width, line_width)
    
    # 调整图片宽度以适应最长的文本行
    width = max(width, int(max_width))

    # 计算图片高度
    height = (len(lines) + 2) * line_height + 2 * padding

    # 创建图片
    image = Image.new('RGB', (width, height), '#ffffff')
    draw = ImageDraw.Draw(image)

    # 绘制背景
    draw.rectangle([0, 0, width, height], fill='#f6f8fa')

    # 绘制 @@ 行
    y = padding
    header_line = diff_text.split('\n')[0]
    draw.text((padding, y), header_line, font=font, fill='#24292e')
    y += line_height

    # 绘制每一行
    for line in lines:
        if not line:
            continue
            
        # 确定行的颜色和前缀
        if line.startswith('-'):
            bg_color = '#ffeef0'
            text_color = '#24292e'
        elif line.startswith('+'):
            bg_color = '#e6ffec'
            text_color = '#24292e'
        else:
            bg_color = None
            text_color = '#24292e'

        # 绘制背景（如果需要）
        if bg_color:
            draw.rectangle([0, y, width, y + line_height], fill=bg_color)

        # 绘制文本
        draw.text((padding, y), line, font=font, fill=text_color)
        y += line_height

    # 转换为字节流
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    
    return img_byte_arr
