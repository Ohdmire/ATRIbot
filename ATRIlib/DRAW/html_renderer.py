import io
import logging
from pathlib import Path

from PIL import Image
from weasyprint import CSS, HTML
import pypdfium2 as pdfium


MAX_RENDER_HEIGHT = 24000
MEASURE_HEIGHT = 120000
MAX_MEASURE_HEIGHT = 1000000
PDF_TO_PX_SCALE = 96 / 72


def _page_css(width: int, height: int, clip_overflow: bool = True) -> CSS:
    overflow = "overflow: hidden;" if clip_overflow else ""
    return CSS(
        string=f"""
        @page {{
            size: {width}px {height}px;
            margin: 0;
        }}

        html, body {{
            margin: 0;
            padding: 0;
            width: {width}px;
            {overflow}
        }}
        """
    )


def _iter_boxes(box):
    yield box
    for child in getattr(box, "children", ()):
        yield from _iter_boxes(child)


def _page_content_height(page) -> float:
    page_box = page._page_box
    root_heights = []
    descendant_bottom = 0
    for box in _iter_boxes(page_box):
        element_tag = getattr(box, "element_tag", None)
        box_bottom = getattr(box, "position_y", 0) + getattr(box, "height", 0)
        if element_tag in ("html", "body"):
            root_heights.append(box_bottom)
        elif getattr(box, "element", None) is not None:
            descendant_bottom = max(descendant_bottom, box_bottom)

    if root_heights:
        root_height = max(root_heights)
        logging.info(f"WeasyPrint root高度: {root_height}")
        logging.info(f"WeasyPrint descendant最大bottom: {descendant_bottom}")
        return root_height

    return descendant_bottom


def _measure_height(html_content: str, base_url: str | Path | None, width: int) -> float:
    measure_height = MEASURE_HEIGHT

    while True:
        document = HTML(string=html_content, base_url=base_url).render(
            stylesheets=[_page_css(width, measure_height, clip_overflow=False)]
        )
        if not document.pages:
            return 1

        if len(document.pages) == 1:
            return max(1, _page_content_height(document.pages[0]))

        logging.info(f"WeasyPrint测量页分页: height={measure_height}, pages={len(document.pages)}")
        if measure_height >= MAX_MEASURE_HEIGHT:
            last_page_height = _page_content_height(document.pages[-1])
            estimated_height = (len(document.pages) - 1) * measure_height + last_page_height
            logging.warning(f"WeasyPrint测量达到上限，估算高度: {estimated_height}")
            return max(1, estimated_height)

        measure_height = min(measure_height * 2, MAX_MEASURE_HEIGHT)


def render_html_to_jpeg(
    html_content: str,
    width: int,
    output_path: str | Path | None = None,
    base_url: str | Path | None = None,
    max_height: int = MAX_RENDER_HEIGHT,
    quality: int = 95,
) -> io.BytesIO:
    body_height = _measure_height(html_content, base_url, width)
    scale = min(1, max_height / body_height)
    final_height = max(1, min(max_height, int(body_height * scale + 0.999)))
    final_width = max(1, int(width * scale + 0.999))

    logging.info(f"WeasyPrint body高度: {body_height}")
    logging.info(f"WeasyPrint缩放系数: {scale}")
    logging.info(f"WeasyPrint最终图片尺寸: {final_width}x{final_height}")

    pdf_bytes = HTML(string=html_content, base_url=base_url).write_pdf(
        stylesheets=[_page_css(width, int(body_height + 0.999))]
    )
    pdf = pdfium.PdfDocument(pdf_bytes)
    try:
        page = pdf[0]
        bitmap = page.render(scale=PDF_TO_PX_SCALE * scale)
        image = bitmap.to_pil().convert("RGB")
    finally:
        pdf.close()

    if image.size != (final_width, final_height):
        image = image.resize((final_width, final_height), Image.Resampling.LANCZOS)

    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format="JPEG", quality=quality, optimize=True, subsampling=0)
    if output_path is not None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        image.save(output_path, format="JPEG", quality=quality, optimize=True, subsampling=0)

    img_byte_arr.seek(0)
    image_size = img_byte_arr.getbuffer().nbytes
    logging.info(f"图片大小: {image_size / 1024 / 1024:.2f} MB")
    return img_byte_arr
