import cv2
import numpy as np

template_width = 58
template_height = 64

def show(image, name='image'):
    cv2.imshow(name, image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def resize(image, width):
    return cv2.resize(image, (width, int(image.shape[0] * width / image.shape[1])))

def process_template(path):
    image = cv2.imread(path)
    # 缩放width = 1000
    image = resize(image, width=500)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # cv2.drawContours(image, contours, -1, (0, 0, 255), 2)

    # 识别最外面的轮廓
    outer_contour = None
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if 1.7 < h / w < 1.8: 
            # cv2.rectangle(image, (x, y), (x+w, y+h), (0, 0, 255), 2)
            outer_contour = (x, y, w, h)
    x, y, w, h = outer_contour
    image = image[y:y+h, x:x+w]
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.inRange(gray, 248, 256)  # 保留偏白色的部分
    edges = cv2.Canny(gray, 1000, 1200)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 识别内部的轮廓
    inner_contours = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if 3.4 < w / h < 3.5: 
            # cv2.rectangle(image, (x, y), (x+w, y+h), (0, 0, 255), 2)
            inner_contours.append((x, y, w, h))
    # input(outer_contours)
    # show(image)

    templates = {}
    num = 1
    for counter in inner_contours:
        x, y, w, h = counter
        y += 2
        h -= 6
        x += 4
        w -= 7
        cell = image[y:y+h, x:x+w]
        for i in range(2):
            for j in range(8):
                icon = cell[int(i * h / 2):int((i+1) * h / 2), int(j * w / 8):int((j+1) * w / 8)]
                icon = resize(icon, width=template_width)
                templates[num] = icon
                # cv2.imwrite(f'dataset/{num}.jpg', icon)
                num += 1
    icon = templates[1]
    icon = np.full_like(icon, (146, 91, 35), dtype=np.uint8)
    templates[0] = icon
    for num, icon in templates.items():
        gray = cv2.cvtColor(icon, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(f'dataset/train/{num}.jpg', gray)
    return templates

def process_image(path, templates):
    image = cv2.imread(path)
    image = resize(image, width=500)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # cv2.drawContours(image, contours, -1, (0, 0, 255), 2)

    # 识别最外面的轮廓
    outer_contour = None
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if 1.4 < h / w < 1.5: 
            # cv2.rectangle(image, (x, y), (x+w, y+h), (0, 0, 255), 2)
            outer_contour = (x, y, w, h)
    x, y, w, h = outer_contour
    x += 10
    w -= 20
    y += 10
    h -= 30
    image = image[y:y+h, x:x+w]
    for i in range(14):
        for j in range(10):
            icon = image[int(i * h / 14):int((i+1) * h / 14), int(j * w / 10):int((j+1) * w / 10)]
            icon = cv2.resize(icon, (template_width, template_height))
            gray = cv2.cvtColor(icon, cv2.COLOR_BGR2GRAY)
            cv2.imwrite(f'dataset/test/{i*10+j}.jpg', gray)
            # show(icon)
            # 匹配模板
            scores = {}
            for idx, template in templates.items():
                res = cv2.matchTemplate(icon, template, cv2.TM_CCOEFF)
                _, score, _, _ = cv2.minMaxLoc(res)
                scores[idx] = score
            sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            icon_idx = sorted_scores[0][0]
            # show(templates[icon_idx])
if __name__ == '__main__':
    templates = process_template('template.jpg')
    # print(templates[0].shape)
    image = process_image('image.jpg', templates)
    # 14 500 1184 2159
    (500-14)/(2159-1184)