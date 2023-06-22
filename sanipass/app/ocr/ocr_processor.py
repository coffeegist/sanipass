from .engines.tesseract import TesseractOCR

from sanipass.logger import logger


class OCRProcessor:

    def __init__(self, **kwargs):
        self.engine = TesseractOCR(**kwargs)


    # Returns a dictionary of OCREntries
    def get_ocr_data(self, image):
        return self.engine.get_ocr_data(image)
