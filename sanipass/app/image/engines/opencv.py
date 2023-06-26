import cv2
import numpy as np
from sanipass.logger import logger

class OpenCV:

    def __init__(self):
        pass


    @staticmethod
    def otsu_binarization(image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        _, imgf = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return imgf

    @staticmethod
    def otsu_inv_binarization(image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        _, imgf = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        return imgf


    @staticmethod
    def adaptive_thresholding(image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (1, 1), 0)
        return cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

    @staticmethod
    def binarization(image):
        return OpenCV.otsu_binarization(image)
        return OpenCV.adaptive_thresholding(image)

    @staticmethod
    def noise_removal(image):
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        except:
            logger.warning("OpenCV.noise_removal:  Unable to convert image to grayscale")
            gray = image
        blur = cv2.medianBlur(gray, 1)
        return cv2.fastNlMeansDenoising(blur, None, 10, 7, 21)


    @staticmethod
    def skeletonization(image):
        kernel = np.ones((1,1),np.uint8)
        erosion = cv2.erode(image,kernel,iterations = 1)
        return cv2.dilate(erosion,kernel,iterations = 1)

    def deskew():
        pass

    def save_image(image, path):
        cv2.imwrite(path, image)

    def open_image(path):
        return cv2.imread(path)

    def perform_preprocessing(image):
        # image = OpenCV.otsu_binarization(image)
        # image = OpenCV.otsu_inv_binarization(image)
        # image = OpenCV.adaptive_thresholding(image)

        # image = OpenCV.noise_removal(image)
        # image = OpenCV.skeletonization(image)

        # cv2.imshow('image', image)

        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
