import docx
from log import logger


def read_docx(docx_path):
    logger.info('Start process docx:...')
    doc = docx.Document(docx_path)
    all_paras = doc.paragraphs
    all_text = ''
    for para in all_paras:
        all_text += para.text
    logger.info("Success process docx.")
    return all_text
