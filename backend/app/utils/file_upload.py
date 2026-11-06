"""文件上传工具"""
import os
import uuid
from datetime import datetime
from fastapi import UploadFile
from app.config import settings


async def save_upload_file(file: UploadFile, subdir: str = "common") -> str:
    """保存上传文件，返回可访问的 URL 路径"""
    if not file.filename:
        return ""

    # 按日期分子目录
    date_dir = datetime.now().strftime("%Y%m%d")
    save_dir = os.path.join(settings.UPLOAD_DIR, subdir, date_dir)
    os.makedirs(save_dir, exist_ok=True)

    # 生成唯一文件名
    ext = os.path.splitext(file.filename)[1] or ""
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(save_dir, filename)

    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)

    return f"/uploads/{subdir}/{date_dir}/{filename}"
