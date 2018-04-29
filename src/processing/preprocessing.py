import cv2
from skimage import feature, exposure
import dlib
from openface import openface

SCALE_FACTOR = 1
predictor_model = "/home/kuzmovych/PycharmProjects/MVI/SP/openface/models/dlib/shape_predictor_68_face_landmarks.dat"
face_detector = dlib.get_frontal_face_detector()


def get_gradient(image):
    return cv2.Laplacian(image, cv2.CV_64F)


def get_hog(image):
    logo = image[:, :]
    logo = cv2.resize(logo, (0, 0), fx=1 / SCALE_FACTOR, fy=1 / SCALE_FACTOR)
    H, hogImage = feature.hog(logo, orientations=9, pixels_per_cell=(16, 16),
                              cells_per_block=(4, 4), transform_sqrt=True, visualise=True)
    hogImage = exposure.rescale_intensity(hogImage, out_range=(0, 255))
    hogImage = hogImage.astype("uint8")
    hogImage = cv2.resize(hogImage, (0, 0), fx=SCALE_FACTOR, fy=SCALE_FACTOR)

    return hogImage


def detect_faces(image):
    detected_faces = face_detector(image, 1)
    return detected_faces


def detect_landmarks(image):
    face_aligner = openface.AlignDlib(predictor_model)
    detected_faces = face_detector(image, 1)
    if detected_faces:
        aligned_face = face_aligner.align(534, image, detected_faces[0],
                                          landmarkIndices=openface.AlignDlib.OUTER_EYES_AND_NOSE)

        return aligned_face
