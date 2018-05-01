import cv2
from skimage import feature, exposure
import dlib
from openface import openface

SCALE_FACTOR = 1
predictor_model = "/home/kuzmovych/PycharmProjects/MVI/SP/openface/models/dlib/shape_predictor_68_face_landmarks.dat"
face_aligner = openface.AlignDlib(predictor_model)
face_detector = dlib.get_frontal_face_detector()


def get_gradient(image):
    return cv2.Laplacian(image, cv2.CV_64F)


def get_hog(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)[:, :]
    gray = cv2.resize(gray, (0, 0), fx=SCALE_FACTOR, fy=SCALE_FACTOR)
    H, hogImage = feature.hog(gray, orientations=9, pixels_per_cell=(16, 16),
                              cells_per_block=(4, 4), transform_sqrt=True, visualise=True)
    hogImage = exposure.rescale_intensity(hogImage, out_range=(0, 255))
    hogImage = hogImage.astype("uint8")
    hogImage = cv2.resize(hogImage, (0, 0), fx=SCALE_FACTOR, fy=SCALE_FACTOR)

    return hogImage


def detect_faces(image):
    detected_faces = face_detector(image, 1)
    return detected_faces


def align_face(image):
    aligned_face = face_aligner.align(534, image, landmarkIndices=openface.AlignDlib.INNER_EYES_AND_BOTTOM_LIP)
    return aligned_face


def show_landmarks(image):
    f = face_detector(image, 1)[0]
    landmarks = face_aligner.findLandmarks(image, f)
    res = image.copy()
    for l in landmarks:
        cv2.circle(res, l, 2, (255, 255, 255), -1)

    return res
