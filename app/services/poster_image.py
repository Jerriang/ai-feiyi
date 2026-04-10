import logging
import textwrap
import uuid
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)


def _load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/usr/share/fonts/truetype/noto/NotoSerifCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSerifSC-Regular.otf",
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for font_path in candidates:
        if Path(font_path).exists():
            try:
                return ImageFont.truetype(font_path, size=size)
            except Exception:
                continue
    logger.warning("Poster font fallback: no Chinese font found, using default font")
    return ImageFont.load_default()


def _style_bg(template_style: str) -> tuple[tuple[int, int, int], tuple[int, int, int]]:
    if template_style == "文艺":
        return (245, 240, 232), (132, 94, 70)
    if template_style == "社媒":
        return (245, 246, 250), (76, 87, 125)
    return (249, 246, 240), (196, 60, 60)  # 国风


def ai_summary(heritage_name: str) -> str:
    text = f"今日沉浸体验{heritage_name}"
    return text[:14]


def render_poster_image(
    heritage_name: str,
    user_nickname: str,
    heritage_image_url: str,
    template_style: str,
    output_dir: Path,
) -> str:
    width, height = 1080, 1620
    bg_color, accent = _style_bg(template_style)
    canvas = Image.new("RGB", (width, height), color=bg_color)
    draw = ImageDraw.Draw(canvas)

    # 宣纸纹理
    for y in range(0, height, 8):
        alpha = 6 if y % 16 == 0 else 3
        draw.line([(0, y), (width, y)], fill=(220, 212, 198, alpha), width=1)

    # 非遗图片占位区域
    image_box = (90, 180, width - 90, 840)
    draw.rounded_rectangle(image_box, radius=26, outline=accent, width=4, fill=(255, 255, 255))
    if heritage_image_url:
        draw.text((image_box[0] + 30, image_box[1] + 30), "非遗项目图", fill=(120, 120, 120), font=_load_font(36))
        draw.text((image_box[0] + 30, image_box[1] + 90), "已检测到图片链接", fill=(120, 120, 120), font=_load_font(28))
    else:
        draw.text((image_box[0] + 30, image_box[1] + 30), "暂无项目图", fill=(120, 120, 120), font=_load_font(32))

    title_font = _load_font(86)
    subtitle_font = _load_font(42)
    meta_font = _load_font(32)

    draw.text((90, 900), heritage_name, fill=(196, 60, 60), font=title_font)
    subtitle = ai_summary(heritage_name)
    draw.text((90, 1020), subtitle, fill=(60, 60, 60), font=subtitle_font)

    today = datetime.now().strftime("%Y-%m-%d")
    meta = f"{user_nickname} · 体验日期 {today}"
    draw.text((90, 1450), meta, fill=(90, 90, 90), font=meta_font)

    # 二维码占位
    qr_x, qr_y, qr_size = width - 280, 1360, 170
    draw.rounded_rectangle((qr_x, qr_y, qr_x + qr_size, qr_y + qr_size), radius=12, outline=accent, width=4, fill=(255, 255, 255))
    draw.text((qr_x + 48, qr_y + 68), "QR", fill=accent, font=_load_font(48))

    output_dir.mkdir(parents=True, exist_ok=True)
    filename = f"poster_{uuid.uuid4().hex[:12]}.png"
    file_path = output_dir / filename
    canvas.save(file_path, format="PNG")
    return filename
