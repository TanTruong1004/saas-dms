from transformers import pipeline
from log import logger

english_transcriber = pipeline("automatic-speech-recognition", model="openai/whisper-tiny")
vietnam_transcriber = pipeline("automatic-speech-recognition", model="vinai/PhoWhisper-small")


class Speech2Text:
    def __init__(self, lang='vn'):
        self.lang = lang

    def stt(self, audio_path: str):
        try:
            logger.info('Start process audio:...')

            if self.lang == 'vn':
                model = vietnam_transcriber
            elif self.lang == 'en':
                model = english_transcriber
            else:
                logger.error(f"Unsupported language {self.lang}")
                return False

            output = model(audio_path)
            logger.info("Success process audio.")
            return output.get('text')
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            return False
