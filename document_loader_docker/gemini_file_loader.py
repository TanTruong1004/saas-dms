from log import logger
from PIL import Image
from io import BytesIO
import google.generativeai as genai
import os
import re
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

if not GEMINI_API_KEY:
    logger.warning("GOOGLE_API_KEY không được tìm thấy trong biến môi trường. Vui lòng kiểm tra tệp .env.")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest")


def sanitize_filename(filename):
    filename = filename.lower()
    filename = re.sub(r'[^a-z0-9\-]', '-', filename)
    filename = filename.strip('-')
    if not filename:
        filename = 'file'
    return filename


def gemini_ocr(pil_image, original_filename='uploaded_image.jpg'):
    _, ext = os.path.splitext(original_filename)
    ext = ext.lower()

    format_mime_map = {
        '.jpeg': ('JPEG', 'image/jpeg'),
        '.jpg': ('JPEG', 'image/jpeg'),
        '.png': ('PNG', 'image/png'),
        '.gif': ('GIF', 'image/gif'),
        '.bmp': ('BMP', 'image/bmp'),
        '.tiff': ('TIFF', 'image/tiff'),
        '.tif': ('TIFF', 'image/tiff'),
    }

    if ext not in format_mime_map:
        logger.warning(f"Định dạng tệp {ext} không được hỗ trợ.")
    format_, mime_type = format_mime_map[ext]
    if format_ == 'JPEG' and (
            pil_image.mode in ('RGBA', 'LA') or (pil_image.mode == 'P' and 'transparency' in pil_image.info)):
        pil_image = pil_image.convert('RGB')
    buffer = BytesIO()
    pil_image.save(buffer, format=format_)
    buffer.seek(0)
    try:
        sample_file = genai.upload_file(buffer, mime_type=mime_type)
    except Exception as e:
        logger.exception(f"Error uploading file: {e}")
        return
    prompt = "Lấy toàn bộ văn bản có trong ảnh cho tôi."
    try:
        response = model.generate_content([sample_file, prompt])
    except Exception as e:
        logger.exception(f"Error generating content: {e}")
        return
    return response.text

