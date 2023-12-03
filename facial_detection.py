import argparse 

import mtcnn
from keras_vggface import VGGFace

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

face_detector = mtcnn.MTCNN()
vggface = VGGFace(model='resnet50', include_top=False, input_shape=(224, 224,3))


def preprocess_image_into_3channel_array(img: Image):
    r, g, b, *_ = img.split()
    three_channel_img = Image.merge('RGB', (r, g, b))

    return np.array(three_channel_img)


def extract_face(img: Image, image_preprocessor):
    img_array = image_preprocessor(img)
    face_roi = face_detector.detect_faces(img_array)

    x1, y1, w, h = face_roi[0]['box']
    face_array = img_array[y1:y1+h, x1:x1+w]

    return face_array

# print(mtcnn.__version__)

if __name__ == "__main__":
    parser = argparse.ArgumentParser('face extractor', '')
    parser.add_argument('image_file', help='Location of image file')  

    args = parser.parse_args() 
    filename = args.image_file 

    ss_photo = Image.open(filename)

    face_bb = extract_face(ss_photo, preprocess_image_into_3channel_array)
    plt.imshow(face_bb)
    plt.show()
