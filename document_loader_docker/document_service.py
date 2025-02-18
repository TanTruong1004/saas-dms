# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
from audio_reader import Speech2Text
from docx_reader import read_docx
from excel_reader import read_excel
from image_reader import process_by_path
from pdf_reader import read_pdf
from pptx_reader import extract_text_from_pptx
from log import logger
from pathlib import Path

app = Flask(__name__)

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({
        'status': 'Success',
        'message': 'Server is running!'
    })

@app.route('/read_doc', methods=['POST'])
def read_doc_handler():
    try:
        logger.info(f"Received request: {request.json}")
        data = request.json
        file_path = data.get('path')
        file_type = data.get('type')
        logger.info(f"Extracted Data from Request: {file_type}, {file_path}")
        if not file_type or not file_path:
            return jsonify({
                'status': 'Fail',
                'text': 'Please provide File path or File type!'
            })
        logger.info("Start processing file.")
        func_dict = {
            'word': read_docx,
            'excel': read_excel,
            'pdf': read_pdf,
            'image': process_by_path,
            'audio': load_audio_reader,
            'pptx': extract_text_from_pptx
        }
        logger.info("Processed File.")
        return jsonify({
            'status': 'Success',
            'text': func_dict[file_type](file_path)
        })
    except Exception as e:
        return jsonify({
            'status': 'Fail',
            'text': f'Error: {str(e)}'
        })


def load_audio_reader(path):
    stt_model = Speech2Text(lang='vn')
    return stt_model.stt(path)


if __name__ == '__main__':
    app.run(debug=False, port=5005, host='0.0.0.0')
