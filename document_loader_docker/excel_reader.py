import pandas as pd
from log import logger


def read_excel(excel_path):
    logger.info('Start process excel:...')
    all_sheets = pd.read_excel(excel_path, sheet_name=None)
    content = ''
    for sheet_name, sheet_data in all_sheets.items():
        content += sheet_name
        content += "\n"
        content += sheet_data.to_string()
        content += "\n"
    logger.info("Success process excel.")
    return content
