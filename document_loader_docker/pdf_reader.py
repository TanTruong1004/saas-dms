from pypdf import PdfReader
from PIL import Image
import io
from log import logger
from const import image_size
from gemini_file_loader import gemini_ocr


def read_pdf(pdf_path):
    logger.info('Start process pdf:...')
    reader = PdfReader(pdf_path)

    text = ''
    for page in reader.pages:
        text += page.extract_text()
        text += read_content_from_image(page)
    logger.info("Success process pdf.")
    return text


def read_content_from_image(pdf_page):
    images = pdf_page.images

    text = ''
    for image in images:
        pil_image = Image.open(io.BytesIO(image.data))
        try:
            text += gemini_ocr(pil_image)
        except:
            continue
    return text


def merge_bound(bounds):
    result = ''
    for box in bounds:
        result += box[1] + ' '
    return result
