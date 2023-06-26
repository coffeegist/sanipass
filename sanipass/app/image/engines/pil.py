import numpy as np
from PIL import Image
from PIL import ImageDraw

class PIL:

    def __init__(self):
        pass


    @staticmethod
    def open_image(path) -> np.ndarray:
        return np.array(Image.open(path))


    @staticmethod
    def draw_rectangle(
        image_array:np.ndarray, left, top, right, bottom,
        outline_color="red",
        fill_color="black"
        ) -> np.ndarray:

        image = Image.fromarray(image_array)
        draw = ImageDraw.Draw(image)
        draw.rectangle(
            [(left, top), (right, bottom)],
            outline=outline_color, fill=fill_color
        )

        return np.array(image)


    @staticmethod
    def save_image(image_array:np.ndarray, path):
        image = Image.fromarray(image_array)
        image.save(path)
