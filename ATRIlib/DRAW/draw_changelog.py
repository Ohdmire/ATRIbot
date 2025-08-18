from playwright.async_api import async_playwright

from ATRIlib.Config import path_config

import logging
import io

css_file_path = path_config.css_file_path
changelog_result_path = path_config.changelog_result_path
changelog_path = path_config.changelog_path

osu_logo_url = "https://i.ppy.sh/32833071ed943a0e11c43168892b4c0322da071b/68747470733a2f2f6f73752e7070792e73682f77696b692f696d616765732f436c69656e742f52656c656173655f73747265616d2f4c617a65722f696d672f6c617a65722e706e673f323032342d31302d3034"

async def html_to_image(title, content, max_body_width=1000):
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
            .header-container {
                display: flex;
                align-items: center;
                margin-bottom: 20px;
            }

            .logo {
                height: 50px;
                margin-right: 15px;
            }

            .custom-text {
                font-size: 24px;
                font-weight: bold;
            }
            .footer-note {
                padding-bottom: 1px;
                border-top: 1px solid #444;
                font-size: 14px;
                color: #888;
                text-align: center;

            }
    """
    html_content += "<style>" + css_style + css_content + "</style>"

    html_content += """<div class="header-container">"""
    html_content += f"""<img class="logo" src="{osu_logo_url}" alt="Logo">"""
    html_content += f"""<div class="custom-text">osu!{title}更新日志</div>"""
    html_content += """</div>"""

    html_content += """<article class="markdown-body">"""
    # html_content += markdown.markdown(content, extensions=['extra'])
    html_content += content
    html_content += """</article>"""

    html_content += """<div class="footer-note">"""
    html_content += """<p>注：本更新日志为AI翻译内容，不代表官方版本，仅供参考</p>"""
    html_content += """</div>"""

    temp_html_path = changelog_path / (title + ".html")

    with open(temp_html_path, 'w') as f:
        f.write(html_content)

    async with async_playwright() as p:
        browser = await p.firefox.launch()
        context = await browser.new_context(viewport={'width': max_body_width, 'height': 1080},
                                            ignore_https_errors=True)
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

        # 滚动回顶部
        await page.evaluate("window.scrollTo(0, 0)")

        max_height = 24000  # 稍微小于32767的值

        if body_height > max_height:
            scale = max_height / body_height
        else:
            scale = 1

        logging.info(f"缩放系数：{scale}")

        # 缩放body元素
        await page.evaluate(f"""
            document.body.style.transform = `scale({scale})`;
            document.body.style.transformOrigin = 'top left';
            """)

        body_height = await page.evaluate("""
                        () => document.body.getBoundingClientRect().height
                    """)

        logging.info(f"最终页面高度: {page_height}")
        logging.info(f"body元素的高度: {body_height}")

        await page.set_viewport_size({"width": max_body_width, "height": page_height})
        screenshot = await page.screenshot(
            path=changelog_result_path / f"{title}.jpg",
            full_page=False,
            type='jpeg',
            quality=95,
            clip={'x': 0, 'y': 0, 'width': max_body_width * scale, 'height': body_height}
        )

        # screenshot_image = Image.open(io.BytesIO(screenshot))

        await browser.close()

        img_byte_arr = io.BytesIO(screenshot)
        img_byte_arr.seek(0)

        image_size = img_byte_arr.getbuffer().nbytes

        logging.info(f"图片大小: {image_size / 1024 / 1024:.2f} MB")

        return img_byte_arr