"""二维码生成工具"""
import os
import uuid
import qrcode
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from app.config import settings


def generate_qr_token() -> str:
    """生成二维码 Token: EQ_ + UUID4"""
    return f"EQ_{uuid.uuid4().hex}"


def generate_qr_code(equipment_code: str, qr_token: str) -> str:
    """
    生成二维码图片并保存到本地，返回图片 URL 路径。
    二维码内容: QRCODE_BASE_URL + token
    """
    qr_url = settings.QRCODE_BASE_URL + qr_token

    # 生成二维码
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # 30% 容错
        box_size=10,
        border=2,
    )
    qr.add_data(qr_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # 转为可编辑的 PIL Image
    img = img.convert("RGB")

    # 在底部添加设备编号文字
    draw = ImageDraw.Draw(img)
    font_paths = [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    font = ImageFont.load_default()
    for fp in font_paths:
        try:
            font = ImageFont.truetype(fp, 24)
            break
        except (IOError, OSError):
            pass

    text = f"设备编号: {equipment_code}"
    # 计算文字宽度
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
    except AttributeError:
        text_width = len(text) * 14

    img_width = img.width
    # 扩展图片高度以容纳文字
    new_height = img.height + 40
    new_img = Image.new("RGB", (img_width, new_height), "white")
    new_img.paste(img, (0, 0))
    draw = ImageDraw.Draw(new_img)
    text_x = (img_width - text_width) // 2
    draw.text((text_x, img.height + 8), text, fill="black", font=font)

    # 保存
    filename = f"{qr_token}.png"
    filepath = os.path.join(settings.QRCODE_DIR, filename)
    new_img.save(filepath, "PNG")

    # 返回访问 URL
    return f"/uploads/qrcodes/{filename}"


def generate_qr_code_bytes(equipment_code: str, qr_token: str) -> bytes:
    """生成二维码图片字节流（用于直接下载/打印）"""
    qr_url = settings.QRCODE_BASE_URL + qr_token
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=2,
    )
    qr.add_data(qr_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

    draw = ImageDraw.Draw(img)
    font_paths = [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    font = ImageFont.load_default()
    for fp in font_paths:
        try:
            font = ImageFont.truetype(fp, 24)
            break
        except (IOError, OSError):
            pass

    text = f"设备编号: {equipment_code}"
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
    except AttributeError:
        text_width = len(text) * 14

    img_width = img.width
    new_height = img.height + 40
    new_img = Image.new("RGB", (img_width, new_height), "white")
    new_img.paste(img, (0, 0))
    draw = ImageDraw.Draw(new_img)
    text_x = (img_width - text_width) // 2
    draw.text((text_x, img.height + 8), text, fill="black", font=font)

    buf = BytesIO()
    new_img.save(buf, format="PNG")
    return buf.getvalue()
