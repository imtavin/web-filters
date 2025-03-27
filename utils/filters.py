import cv2
import numpy as np


WRITE_PATH = 'static/filters/image.png'
DOWNLOAD_PATH = 'filters/image.png'

def gray(path):
    # Carregar imagem colorida
    img_color = cv2.imread(path)
    gray_image = cv2.cvtColor(img_color, cv2.COLOR_BGR2GRAY)

    cv2.imwrite(WRITE_PATH, gray_image)

    return DOWNLOAD_PATH


def blur(path):
    # Carregar imagem colorida
    img_color = cv2.imread(path)
    blurred_img = cv2.GaussianBlur(img_color, (5, 5), 0)

    cv2.imwrite(WRITE_PATH, blurred_img)

    return DOWNLOAD_PATH

def thresholding(path):
    # Carregar imagem colorida
    img_color = cv2.imread(path)
    _ , thresh_img = cv2.threshold(img_color, 120, 255, cv2.THRESH_TOZERO)

    cv2.imwrite(WRITE_PATH, thresh_img)

    return DOWNLOAD_PATH

def erode(path):
    # Carregar imagem colorida
    img_color = cv2.imread(path)
    kernel = np.ones((5, 5), np.uint8) 
    erosion_img = cv2.erode(img_color, kernel, iterations=1) 

    cv2.imwrite(WRITE_PATH, erosion_img)

    return DOWNLOAD_PATH

def dilate(path):
    # Carregar imagem colorida
    img_color = cv2.imread(path)
    kernel = np.ones((5, 5), np.uint8) 
    dilation_img = cv2.dilate(img_color, kernel, iterations=1) 

    cv2.imwrite(WRITE_PATH, dilation_img)

    return DOWNLOAD_PATH

def open(path):
    # Carregar imagem colorida
    img_color = cv2.imread(path)
    kernel = np.ones((3, 3), np.uint8) 
    opening_img = cv2.morphologyEx(img_color, cv2.MORPH_OPEN, kernel, iterations=1) 

    cv2.imwrite(WRITE_PATH, opening_img)

    return DOWNLOAD_PATH

def close(path):
    # Carregar imagem colorida
    img_color = cv2.imread(path)
    kernel = np.ones((3, 3), np.uint8) 
    closing_img = cv2.morphologyEx(img_color, cv2.MORPH_CLOSE, kernel, iterations=1) 

    cv2.imwrite(WRITE_PATH, closing_img)

    return DOWNLOAD_PATH