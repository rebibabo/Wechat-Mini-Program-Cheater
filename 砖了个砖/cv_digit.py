import cv2
import numpy as np
from PIL import Image

def find_matches(template_path, image_path):
    template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    res = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
    threshold = 0.9
    loc = np.where(res >= threshold)
    return zip(*loc[::-1])

def crop(ori_path, template_path, choice):
    if choice == 0:
        image = Image.open(ori_path)
        pic_range = (36, 523, 1160, 2120)
        result = image.crop(pic_range)
        result.save(template_path)
    elif choice == 1:
        image = cv2.imread(ori_path)
        image = image[int(image.shape[0] * 0.18):int(image.shape[0] * 0.82), :]
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(image, contours, -1, (0, 255, 0), 2)
        mask = np.zeros_like(gray)
        cv2.drawContours(mask, contours, -1, (255), -1)
        result = np.zeros_like(image)
        result[mask == 255] = image[mask == 255]
        result = result[int(result.shape[0] * 0.026):int(result.shape[0] * 0.96), int(result.shape[1] * 0.03):int(result.shape[1] * 0.97)]
        cv2.imwrite('result.jpg', result)

def recognize_digit(ori_path):
    template_path = 'image/template.jpg'
    crop(ori_path, template_path, 1)
    image = Image.open(template_path)
    num_coord = [[0 for _ in range(10)] for _ in range(14)]
    for i in range(1, 48):
        image_path = f'image/{i}.jpg'
        matches = find_matches(template_path, image_path)
        # print(f'{i}: {list(matches)}')
        width, height = image.size
        cell_width = width / 10
        cell_height = height / 14
        for match in matches:
            x, y = match
            x = int(x / cell_width)
            y = int(y / cell_height)
            num_coord[y][x] = i
    return num_coord

if __name__ == '__main__':
    num_coord = recognize_digit('image.jpg')
    input(num_coord)