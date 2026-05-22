from ATRIlib.Config import path_config
from ATRIlib.DRAW.html_renderer import render_html_to_jpeg

css_file_path = path_config.css_file_path
changelog_result_path = path_config.changelog_result_path
changelog_path = path_config.changelog_path

osu_logo_url = "https://i.ppy.sh/32833071ed943a0e11c43168892b4c0322da071b/68747470733a2f2f6f73752e7070792e73682f77696b692f696d616765732f436c69656e742f52656c656173655f73747265616d2f4c617a65722f696d672f6c617a65722e706e673f323032342d31302d3034"

async def html_to_image(title, content, max_body_width=1000):
    with open(css_file_path / "github-markdown-dark.css", 'r') as file:
        css_content = file.read()

    # 修改content 把注释内容添加为标签
    content = content.replace("[INDENT]", '<div style="margin-left: 20px;">')
    content = content.replace("[/INDENT]", '</div>')

    html_content = """
        <!doctype html>
        <html>
        <head>
        <meta name="color-scheme" content="dark">
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="github-markdown-dark.css">

        """
    css_style = """
            html, body {
                background: #0d1117;
            }

            body {
                color: #f0f6fc;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            }

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
                padding: 24px 45px 0;
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
    html_content += "</head><body>"

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
    html_content += "</body></html>"

    temp_html_path = changelog_path / (title + ".html")

    with open(temp_html_path, 'w') as f:
        f.write(html_content)

    return render_html_to_jpeg(
        html_content,
        width=max_body_width,
        output_path=changelog_result_path / f"{title}.jpg",
        base_url=temp_html_path.parent,
        quality=95,
    )
