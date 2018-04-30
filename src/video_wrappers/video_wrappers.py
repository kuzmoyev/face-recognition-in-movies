import cv2
from itertools import count


class BaseVideo:
    cv_class = None

    def __init__(self, file_name, **kwargs):
        self.file_name = file_name
        self.video = self.cv_class(file_name, **kwargs) if file_name is not None else None

    @property
    def width(self):
        return int(self.video.get(cv2.CAP_PROP_FRAME_WIDTH))

    @property
    def height(self):
        return int(self.video.get(cv2.CAP_PROP_FRAME_HEIGHT))

    @property
    def fps(self):
        return int(self.video.get(cv2.CAP_PROP_FPS))

    @property
    def current_position(self):
        return int(self.video.get(cv2.CAP_PROP_POS_MSEC)) // 1000

    @property
    def fourcc(self):
        return int(self.video.get(cv2.CAP_PROP_FOURCC))

    @property
    def parameters(self):
        """Used to create VideoWriter with the same parameters"""
        return {
            'fps': self.fps,
            'width': self.width,
            'height': self.height,
            'fourcc': self.fourcc
        }

    @property
    def frames_count(self):
        if self.file_name == 0:
            # Web cam
            return 0
        else:
            return int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))

    @property
    def video_length(self):
        if self.file_name == 0:
            # Web cam
            return 0
        else:
            return int(self.frames_count / self.fps)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.video:
            self.video.release()

    def __str__(self):
        return f'{self.width}x{self.height} {self.fps}fps, {self.frames_count}frames, {self.video_length}s'


class VideoReader(BaseVideo):
    cv_class = cv2.VideoCapture

    def __init__(self, file_name_or_device_index):
        super().__init__(file_name_or_device_index)

    def frames(self, max_time=None, return_frame_count=False):
        """Generator that yields frames until there are any.

        :param max_time: time limit in seconds. 0 or None means no time limit.
        :param return_frame_count: whether to return frame number.
        """

        for f in count():
            ret, frame = self.video.read()
            if ret:
                if return_frame_count:
                    yield f, frame
                else:
                    yield frame
            else:
                break

            if max_time and f >= max_time * self.fps:
                break


class VideoWriter(BaseVideo):
    cv_class = cv2.VideoWriter

    DEFAULT_CODEC = cv2.VideoWriter_fourcc(*'MJPG')

    def __init__(self, file_name, fourcc=DEFAULT_CODEC, fps=30, width=0, height=0):
        super().__init__(file_name, fourcc=fourcc, fps=fps, frameSize=(width, height))

    def write(self, frame):
        if self.video:
            self.video.write(frame)

    def active(self):
        return self.video is not None
