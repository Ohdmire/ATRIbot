import markdown
from ATRIlib.Config import path_config
from ATRIlib.DRAW.html_renderer import render_html_to_jpeg

news_path = path_config.news_path
news_result_path = path_config.news_result_path
css_file_path = path_config.css_file_path

async def draw_news(title,translated_content):
    result = await html_to_image(title,translated_content)
    return result

async def html_to_image(title,translated_content,max_body_width=800):

    with open(css_file_path / "github-markdown-dark.css", 'r') as file:
        css_content = file.read()

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
    html_content += "</head><body>"

    html_content += """<article class="markdown-body">"""
    html_content += markdown.markdown(translated_content,extensions=['extra'])
    html_content += """</article>"""
    html_content += "</body></html>"


    temp_html_path = news_path / (title + ".html")

    with open(temp_html_path,'w') as f:
        f.write(html_content)

    return render_html_to_jpeg(
        html_content,
        width=max_body_width,
        output_path=news_result_path / f"{title}.jpg",
        base_url=temp_html_path.parent,
        quality=95,
    )
