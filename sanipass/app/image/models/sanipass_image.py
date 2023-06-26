from typing import List
from pathlib import Path
import cv2
import numpy as np

from sanipass.app.image.models.ocr_entry import OCREntry
from sanipass.app.image.engines.opencv import OpenCV
from sanipass.app.image.engines.pil import PIL
from sanipass.logger import logger

class SanipassImage:

    def __init__(self, path:str):
        self.path = path
        self.engine = PIL
        self.image = self.engine.open_image(path)
        self.ocr_entries = []


    def _get_intermediate_filename(self, intermediate_step):
        path= Path(self.path)
        return str(path.absolute()).replace(
            path.suffix, f'-{intermediate_step}{path.suffix}'
        )


    def perform_preprocessing(self, save_preprocessing_image=False):
        #self.image = cv2.imread(self.image)
        self.image = OpenCV.perform_preprocessing(self.image)

        if save_preprocessing_image:
            self.engine.save_image(self.image, self._get_intermediate_filename('preprocessed'))


    def add_ocr_entries(self, ocr_entries:List):
        self.ocr_entries.extend(ocr_entries)


    def get_sensitive_ocr_entries(self):
        return [entry for entry in self.ocr_entries if entry.sensitive]


    def redact_sensitive_data(self, outline_color="red", fill_color="black"):
         for entry in self.ocr_entries:
            if entry.sensitive:
                self.redact_entry(entry, outline_color, fill_color)


    def redact_entry(self, ocr_entry:OCREntry, outline_color="red", fill_color="black"):
        #image = self.engine.open_image(self.path)

        if ocr_entry.sensitive_match == ocr_entry.text:
            logger.debug(f'Redacting exact match {ocr_entry.text}')
            self.image = self.engine.draw_rectangle(
                self.image,
                left=ocr_entry.left,
                top=ocr_entry.top,
                right=ocr_entry.left + ocr_entry.width,
                bottom=ocr_entry.top + ocr_entry.height,
                outline_color=outline_color, fill_color=fill_color)
        else:
            # Get the coordinates of the word
            left = ocr_entry.left
            top = ocr_entry.top
            height = ocr_entry.height

            # Calculate the bounding box of the sensitive word
            text_start = ocr_entry.text.index(ocr_entry.sensitive_match)
            text_end = text_start + len(ocr_entry.sensitive_match)

            word_left = left
            character_width = ocr_entry.width / len(ocr_entry.text)
            for j in range(text_start):
                word_left += character_width

            word_top = top
            word_width = character_width * len(ocr_entry.sensitive_match)
            word_height = height

            # Draw a rectangle around the word
            self.image = self.engine.draw_rectangle(
                self.image,
                left=word_left,
                top=word_top,
                right=word_left + word_width,
                bottom=word_top + word_height,
                outline_color=outline_color, fill_color=fill_color)


    def save(self, path=None, overwrite=False):
        if path is None:
            path = self.path

        if not overwrite:
            if Path(path).exists():
                raise FileExistsError(f'File already exists: {path}')

        self.engine.save_image(self.image, path)
