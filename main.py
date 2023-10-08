import cv2
import numpy as np
from tensorflow import keras
import tensorflow as tf


def letters_extract(image_file: str, out_size=28):
    img = cv2.imread(image_file)
    # img = cv2.medianBlur(img, 7)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    ret, thresh = cv2.threshold(gray, 90, 255, cv2.THRESH_BINARY)
    # thresh = cv2.UMat(100)
    img_erode = cv2.erode(thresh, np.ones((3, 3), np.uint8), iterations=1)

    # Get contours
    contours, hierarchy = cv2.findContours(img_erode, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    # contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    output = img.copy()

    letters = []

    for idx, contour in enumerate(contours):
        (x, y, w, h) = cv2.boundingRect(contour)
        print("R", idx, x, y, w, h, cv2.contourArea(contour), hierarchy[0][idx])
        # hierarchy[i][0]: the index of the next contour of the same level
        # hierarchy[i][1]: the index of the previous contour of the same level
        # hierarchy[i][2]: the index of the first child
        # hierarchy[i][3]: the index of the parent

        if hierarchy[0][idx][3] == 0:
            cv2.rectangle(output, (x, y), (x + w, y + h), (70, 0, 0), 1)
            letter_crop = gray[y:y + h, x:x + w]
            # print(letter_crop.shape)

            # Resize letter canvas to square
            size_max = max(w, h)
            letter_square = 255 * np.ones(shape=[size_max, size_max], dtype=np.uint8)
            if w > h:
                # Enlarge image top-bottom
                # ------
                # ======
                # ------
                y_pos = size_max // 2 - h // 2
                letter_square[y_pos:y_pos + h, 0:w] = letter_crop
            elif w < h:
                # Enlarge image left-right
                # --||--
                x_pos = size_max // 2 - w // 2
                letter_square[0:h, x_pos:x_pos + w] = letter_crop
            else:
                letter_square = letter_crop

            # Resize letter to 28x28 and add letter and its X-coordinate
            letters.append((x, w, cv2.resize(letter_square, (out_size, out_size), interpolation=cv2.INTER_AREA)))

    # Sort array in place by X-coordinate
    letters.sort(key=lambda x: x[0], reverse=False)

    return letters, output, img_erode


# cv2.imshow("Input", img)
# cv2.imshow("Enlarged", thresh)
# cv2.imshow("Enlarged1", img_erode)
# cv2.imshow("Output", output)
#
# letters, img, output = letters_extract('test1.png')
#
# cv2.imshow('img', img)
# cv2.imshow('out', output)
#
# for i in range(len(letters)):
#     cv2.imshow(f'{i}', letters[i][2])
# # cv2.imshow("0", letters[0][2])
# # cv2.imshow("1", letters[1][2])
# # cv2.imshow("2", letters[2][2])
# # cv2.imshow("3", letters[3][2])
# # cv2.imshow("4", letters[4][2])
# cv2.waitKey(0)

emnist_labels = [48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80,
                 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109,
                 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122]


def emnist_predict_img(model, img):
    img_arr = np.expand_dims(img, axis=0)
    img_arr = 1 - img_arr / 255.0
    img_arr[0] = np.rot90(img_arr[0], 3)
    img_arr[0] = np.fliplr(img_arr[0])
    img_arr = img_arr.reshape((1, 28, 28, 1))

    predict = model.predict([img_arr])
    result = np.argmax(predict, axis=1)
    return chr(emnist_labels[result[0]])


outs = []
errs = []


def img_to_str(model, image_file: str):
    letters, out, err = letters_extract(image_file)
    outs.append(out)
    errs.append(err)
    s_out = ""
    for i in range(len(letters)):
        dn = letters[i + 1][0] - letters[i][0] - letters[i][1] if i < len(letters) - 1 else 0

        s_out += emnist_predict_img(model, letters[i][2])
        if (dn > letters[i][1] / 4):
            s_out += ' '

    return s_out


model = keras.models.load_model("data/weights/emnist_letters3_0.h5")

s_out = img_to_str(model, "data\\testing\\test2.png")
print(s_out)

for i in range(len(outs)):
    cv2.imshow(f"{i}", outs[i])
    cv2.imshow(f"{i}{i}", errs[i])
cv2.waitKey(0)
