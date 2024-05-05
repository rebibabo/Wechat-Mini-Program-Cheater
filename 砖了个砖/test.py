import cv2
import os
import numpy as np
 
def calculate(image1, image2):
    # 灰度直方图算法
    # 计算单通道的直方图的相似值
    hist1 = cv2.calcHist([image1], [0], None, [256], [0.0, 255.0])
    hist2 = cv2.calcHist([image2], [0], None, [256], [0.0, 255.0])
    # 计算直方图的重合度
    degree = 0
    for i in range(len(hist1)):
        if hist1[i] != hist2[i]:
            degree = degree + \
                (1 - abs(hist1[i] - hist2[i]) / max(hist1[i], hist2[i]))
        else:
            degree = degree + 1
    degree = degree / len(hist1)
    return degree[0]
 

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

if __name__ == "__main__":
    templates_imgs = []
    imgs = []
    for pic in os.listdir('image'):
        templates_imgs.append(f'image/{pic}')
    for pic in os.listdir('temp'):
        imgs.append(f'temp/{pic}')
    for img in imgs:
        similarity = []
        for template_img in templates_imgs:
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
        # print(f'{img} is most similar to {templates_imgs[max_index]} with similarity {max_sim}')
        # input()

def recognize_digit2(ori_path):
    template_path = 'image/template.jpg'
    crop(ori_path, template_path, 1)
    templates_imgs = []
    imgs = []
    for pic in os.listdir('image'):
        templates_imgs.append(f'image/{pic}')
    for pic in os.listdir('temp'):
        imgs.append(f'temp/{pic}')
    for img in imgs:
        similarity = []
        for template_img in templates_imgs:
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