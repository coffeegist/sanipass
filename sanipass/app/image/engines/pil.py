from PIL import Image
from PIL import ImageDraw

class PIL:

    def __init__(self):
        pass


    @staticmethod
    def open_image(path):
        return Image.open(path)


    @staticmethod
    def draw_rectangle(image, left, top, right, bottom, outline_color="red", fill_color="black"):
        draw = ImageDraw.Draw(image, 'RGBA')
        draw.rectangle([(left, top), (right, bottom)], outline=outline_color, fill=fill_color)


    @staticmethod
    def save_image(image, path):
        image.save(path)
