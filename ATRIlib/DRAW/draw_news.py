import markdown
from playwright.async_api import async_playwright
from ATRIlib.TOOLS.Download import news_path
import logging
from pathlib import Path
import io

news_result_path = Path('./data/tmp/news')
css_file_path = Path('./data/css/')

async def draw_news(title,translated_content):
    result = await html_to_image(title,translated_content)
    return result

async def html_to_image(title,translated_content,max_body_width=800):

    with open(css_file_path / "github-markdown-dark.css", 'r') as file:
        css_content = file.read()

    html_content = """
        <meta name="color-scheme" content="dark">
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="github-markdown-dark.css">
        
        """
    css_style = """
            .markdown-body {
                box-sizing: border-box;
                min-width: 200px;
                max-width: 980px;
                margin: 0 auto;
                padding: 45px;
            }

            @media (max-width: 767px) {
                .markdown-body {
                    padding: 15px;
                }
            }
    """
    html_content += "<style>" + css_style + css_content + "</style>"

    html_content += """<article class="markdown-body">"""
    html_content += markdown.markdown(translated_content)
    html_content += """</article>"""


    temp_html_path = news_path / (title + ".html")

    with open(temp_html_path,'w') as f:
        f.write(html_content)

    async with async_playwright() as p:
        browser = await p.firefox.launch()
        context = await browser.new_context(viewport={'width': max_body_width, 'height': 1080})
        page = await context.new_page()
        try:
            await page.goto(f"file://{temp_html_path.absolute()}")
        except Exception as e:
            logging.warning(f"页面初始化错误: {e}")

        # 等待页面加载完成
        try:
            await page.wait_for_load_state('domcontentloaded')
        except Exception as e:
            logging.warning(f"页面加载错误: {e}")

        # 缓慢滚动到页面底部并返回总高度
        page_height = await page.evaluate("""
            () => {
                return new Promise((resolve) => {
                    let totalHeight = 0;
                    let distance = 300;
                    let timer = setInterval(() => {
                        let scrollHeight = document.body.scrollHeight;
                        window.scrollBy(0, distance);
                        totalHeight += distance;
                        if(totalHeight >= scrollHeight){
                            clearInterval(timer);
                            resolve(totalHeight);
                        }
                    }, 1);
                });
            }
        """)

        body_height = await page.evaluate("""
            () => document.body.getBoundingClientRect().height
        """)


        await page.set_viewport_size({"width": max_body_width, "height": page_height})
        screenshot = await page.screenshot(
            path = news_result_path / f"{title}.jpg",
            full_page=False,
            type='jpeg',
            quality=95,
            clip={'x': 0, 'y': 0, 'width': max_body_width, 'height': body_height}
            )

        # screenshot_image = Image.open(io.BytesIO(screenshot))

        await browser.close()

        img_byte_arr = io.BytesIO(screenshot)
        img_byte_arr.seek(0)

        image_size = img_byte_arr.getbuffer().nbytes

        logging.info(f"图片大小: {image_size / 1024 / 1024:.2f} MB")

        return img_byte_arr