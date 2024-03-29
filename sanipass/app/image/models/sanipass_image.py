from typing import List, Tuple
from pathlib import Path

from sanipass.app.image.models.ocr_entry import OCREntry
from sanipass.app.image.engines.pil import PIL
from sanipass.logger import logger

# TODO: Redbox whole string, blackbox using keep first / last
class SanipassImage:

    def __init__(self, path):
        self.path:str = path
        self.engine = PIL
        self.image = self.engine.open_image(path)
        self.ocr_entries = []
        self.highlight_entries = []


    def add_ocr_entries(self, ocr_entries:List[OCREntry]):
        logger.debug([f"'{entry.text}' - ({entry.left}, {entry.top}, {entry.width}, {entry.height})" for entry in ocr_entries])
        self.ocr_entries.extend(ocr_entries)


    def get_sensitive_ocr_entries(self):
        return [entry for entry in self.ocr_entries if entry.sensitive]


    def redact_sensitive_data(self, outline_color="red", fill_color="black",
        keep_first=0, keep_last=0, border_width=3, border_padding=2):

        for entry in self.ocr_entries:
            if entry.sensitive:
                self.redact_entry(entry, outline_color, fill_color, keep_first, keep_last, border_width, border_padding)


    def calculate_bounding_box(self, match, entry:OCREntry, keep_first=0, keep_last=0) \
        -> Tuple[int, int, int, int]:

        left = 0
        top = 0
        right = 0
        bottom = 0
        character_width = entry.width / len(entry.text)

        if match == entry.text:
            logger.debug(f'Redacting exact match {match}')


            left = entry.left
            top = entry.top
            right = entry.left + entry.width
            bottom = entry.top + entry.height
        else:
            logger.debug(f'Redacting {match} in entry {entry.text}')
            # Get the coordinates of the word
            word_left = entry.left
            word_top = entry.top
            height = entry.height

            # Calculate the bounding box of the sensitive word
            if match in entry.text:
                text_start = entry.text.index(match)
                text_end = text_start + len(match)
            else:
                text_start = 0
                text_end = len(entry.text)

            for j in range(text_start):
                word_left += character_width

            word_width = character_width * len(match)
            word_height = height

            left = word_left
            top = word_top
            right = word_left + word_width
            bottom = word_top + word_height

        left += keep_first * character_width
        right -= keep_last * character_width
        return (left, top, right, bottom)


    def redact_entry(self, ocr_entry:OCREntry, outline_color="red",
        fill_color="black", keep_first=0, keep_last=0,
        border_width=3, border_padding=2):

        if self.image.mode == 'RGBA':
            self.image = self.image.convert('RGB')

        for match in ocr_entry.sensitive_match:
            # Draw the red box
            (left, top, right, bottom) = self.calculate_bounding_box(match, ocr_entry)
            self.engine.draw_rectangle(
                self.image,
                left=left,
                top=top,
                right=right,
                bottom=bottom,
                outline_color=outline_color,
                border_width = border_width,
                border_padding = border_padding
            )

            if fill_color:
                # Draw the black box
                (left, top, right, bottom) = self.calculate_bounding_box(match, ocr_entry, keep_first, keep_last)
                self.engine.draw_rectangle(
                    self.image,
                    left=left,
                    top=top,
                    right=right,
                    bottom=bottom,
                    fill_color=fill_color,
                    border_width = border_width,
                    border_padding = border_padding
                )


    def save(self, path=None, overwrite=False):
        if path is None:
            path = self.path

        if not overwrite:
            if Path(path).exists():
                raise FileExistsError(f'File already exists: {path}')

        self.engine.save_image(self.image, path)
