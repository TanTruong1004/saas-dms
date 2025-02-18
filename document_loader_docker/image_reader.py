import easyocr
from log import logger
from PIL import Image
from const import image_size
import numpy as np
from gemini_file_loader import gemini_ocr
from pathlib import Path
import os


def process_by_path(path):
    file_name = os.path.basename(path)
    logger.info('Start process image:...')
    image = Image.open(path)
    text = gemini_ocr(image, file_name)
    logger.info("Success process image.")
    return text


def process_by_image(image):
    logger.info('Start process image:...')
    image = image.resize(image_size)
    logger.info("Success process image.")
    text = gemini_ocr(image)
    return text
