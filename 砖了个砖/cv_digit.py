import cv2
import numpy as np
from PIL import Image
import os
from tqdm import tqdm

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
        cv2.imwrite(template_path, result)

def calculate(image1, image2):
    hist1 = cv2.calcHist([image1], [0], None, [256], [0.0, 255.0])
    hist2 = cv2.calcHist([image2], [0], None, [256], [0.0, 255.0])
    max_vals = np.maximum(hist1, hist2)
    epsilon = 1e-10
    max_vals[max_vals == 0] = epsilon
    abs_diff = np.abs(hist1 - hist2)
    degree = np.sum(np.where(hist1 != hist2, 1 - abs_diff / max_vals, 1))
    degree = degree / len(hist1)
    return degree

def classify_hist_with_split(image1, image2, size=(256, 256)):
    image1 = cv2.resize(image1, size)
    image2 = cv2.resize(image2, size)
    sub_image1 = cv2.split(image1)
    sub_image2 = cv2.split(image2)
    sub_data = 0
    for im1, im2 in zip(sub_image1, sub_image2):
        sub_data += calculate(im1, im2)
    sub_data = sub_data / 3
    return sub_data

def recognize_digit(ori_path):
    template_path = 'image/template.jpg'
    crop(ori_path, template_path, 1)
    image = Image.open(template_path)
    width, height = image.size
    cell_width = width / 10
    cell_height = height / 14
    os.makedirs('temp', exist_ok=True)
    for i in range(14):
        for j in range(10):
            x = int(j * cell_width)
            y = int(i * cell_height)
            cell = image.crop((x, y, x + cell_width, y + cell_height))
            cell.save(f'temp/{i*10+j+1}.jpg')
    templates_imgs, imgs = [], []
    num_coord = [[0 for _ in range(10)] for _ in range(14)]
    for pic in os.listdir('image'):
        if pic != 'template.jpg':
            templates_imgs.append((f'image/{pic}', int(pic.split('.')[0])))
    for pic in os.listdir('temp'):
        imgs.append(f'temp/{pic}')
    for img in tqdm(imgs, total=len(imgs)):
        similarity = []
        for template_img, idx in templates_imgs:
            img1 = cv2.imread(img)
            # 将img1裁剪周围10%的边缘
            margin = 0.1
            img1 = img1[int(img1.shape[0] * margin):int(img1.shape[0] * (1-margin)), int(img1.shape[1] * margin):int(img1.shape[1] * (1-margin))]
            img2 = cv2.imread(template_img)
            sim = classify_hist_with_split(img1, img2)
            # print(f'{img} and {template_img} similarity: {sim}')
            similarity.append(sim)
        similarity = np.array(similarity)
        max_sim = np.max(similarity)
        max_index = np.argmax(similarity)
        x = (int(img.split('/')[-1].split('.')[0])-1) // 10
        y = (int(img.split('/')[-1].split('.')[0])-1) % 10
        num_coord[x][y] = templates_imgs[max_index][1]
        # print(f'{img} is most similar to {templates_imgs[max_index]} with similarity {max_sim}')
        # print(x, y, templates_imgs[max_index][1])
        # input()
    return num_coord
    

if __name__ == '__main__':
    num_coord = recognize_digit('680f088e603007d3ba061d410fe8fbb.jpg')
    print(num_coord)