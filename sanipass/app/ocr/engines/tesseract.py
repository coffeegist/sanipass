import string

import pytesseract
from pytesseract import Output
from sanipass.app.image.models.ocr_entry import OCREntry

from sanipass.logger import logger

class TesseractOCR:

    def __init__(
            self, user_words=None, user_patterns=None,
            confidence_threshold=0#, sensitive_data_file=None,
        ):

        self.user_words = user_words
        self.user_patterns = user_patterns
        self.psm = '6'
        self.whitelisted_characters = self._get_whitelisted_characters()
        self.confidence_threshold = confidence_threshold
        self.config = self._get_configuration()


    def _get_whitelisted_characters(self):
        blacklist = '\'"`;:/.,\\|[]{}()'
        whitelist = string.ascii_letters + string.digits

        for character in blacklist:
            whitelist = whitelist.replace(character, '')

        return whitelist


    def _get_configuration(self):
        config = ''

        if self.user_words:
            config += f' --user-words {self.user_words}'

        if self.user_patterns:
            config += f' --user-patterns {self.user_patterns}'

        if self.whitelisted_characters:
          config += f' tessedit_char_whitelist=\'{self.whitelisted_characters}\''

        config += f' --psm {self.psm}'
        config += ' -c preserve_interword_spaces=1' # Unsure on this

        return config


    def get_ocr_data(self, image):
        # Perform OCR on the image
        ocr_entries = []

        logger.debug(f'TesseractOCR.get_ocr_data:  Tesseract Config: {self.config}')
        logger.info(f'TesseractOCR.get_ocr_data:  Processing {image}')
        ocr_data = pytesseract.image_to_data(image, output_type=Output.DICT, config=self.config)

        for entry in range(len(ocr_data['text'])):
            ocr_entries.append(
                OCREntry(
                    text=ocr_data['text'][entry],
                    left=ocr_data['left'][entry],
                    top=ocr_data['top'][entry],
                    width=ocr_data['width'][entry],
                    height=ocr_data['height'][entry],
                    confidence=ocr_data['conf'][entry]
                )
            )

        return ocr_entries
