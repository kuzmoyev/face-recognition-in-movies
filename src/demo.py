import numpy as np

from video_wrappers.video_wrappers import VideoReader, VideoWriter
from processing import preprocessing
import cv2

IMG = '/home/kuzmovych/PycharmProjects/MVI/SP/report/img/tilted.jpg'
img = cv2.imread(IMG)

res = preprocessing.show_landmarks(img)
cv2.imwrite('/home/kuzmovych/PycharmProjects/MVI/SP/report/img/landmarks_tilted.jpg', res)

exit()

SECONDS = 15

with VideoReader(0) as reader, VideoWriter('hog.avi', **reader.parameters) as writer:
    for f, frame in reader.frames(max_time=SECONDS, return_frame_count=True):
        hog = preprocessing.align_face(frame)

        cv2.imshow('frame', hog)
        cv2.waitKey(1)

        hog = cv2.resize(hog, (reader.width, reader.height))
        writer.write(frame)
        writer.write(hog)

        print(f'{f}/{SECONDS * reader.fps}')
        if f == 1:
            break
