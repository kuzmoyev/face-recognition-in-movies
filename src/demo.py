import numpy as np

from video_wrappers.video_wrappers import VideoReader, VideoWriter
from processing import preprocessing
import cv2

SECONDS = 15

with VideoReader(0) as reader, VideoWriter('out.avi', **reader.parameters) as writer:

    for f, frame in reader.frames(max_time=SECONDS, return_frame_count=True):
        hog = preprocessing.get_gradient(frame).astype(np.uint8)

        cv2.imshow('frame', hog)
        cv2.waitKey(1)

        # hog = cv2.resize(hog, (reader.width, reader.height))
        # writer.write(hog)

        print(f'{f}/{SECONDS * reader.fps}')
