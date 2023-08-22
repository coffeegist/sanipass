from PIL import Image
from PIL import ImageDraw

class PIL:

    def __init__(self):
        pass


    @staticmethod
    def open_image(path):
        return Image.open(path)


    @staticmethod
    def draw_rectangle(image, left, top, right, bottom, outline_color=None,
        fill_color=None, border_width=3, border_padding=2):

        border_addends = (border_width + border_padding)

        # We're drawing a highlighting box, add padding
        if fill_color is None:
            left -= border_addends
            top -= border_addends
            right += border_addends
            bottom += border_addends

        draw = ImageDraw.Draw(image, 'RGBA')
        draw.rectangle([(left, top), (right, bottom)], outline=outline_color, fill=fill_color, width=border_width)


    @staticmethod
    def save_image(image, path):
        image.save(path)
