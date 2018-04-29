from video_wrappers.video_wrappers import VideoReader, VideoWriter

import cv2
import face_recognition

from tqdm import tqdm
import logging

log = logging.getLogger()

PB_FMT = '{desc}: {percentage:3.02f}% |{bar}| ' \
         '{n_fmt}/{total_fmt} [passed - {elapsed} | left ~ {remaining} | {rate_fmt}]'


class FaceRecognizer:
    def __init__(self,
                 show=True,
                 highlight_faces=False,
                 frame_scale=0.25,
                 ):

        self.show = show
        self.highlight_faces = highlight_faces
        self.frame_scale = frame_scale

    def process(self, input_video, cast_photos, output_video=None):
        log.i('Starting processing.')

        known_face_names, known_face_encodings = self._encode_cast_photos(cast_photos)

        with VideoReader(input_video) as reader, VideoWriter(output_video, **reader.parameters) as writer:
            frames = reader.frames(return_frame_count=True)
            total_frames = reader.frames_count
            pbar = tqdm(frames, desc='Progress', total=total_frames, unit='frame', bar_format=PB_FMT)
            for f, frame in pbar:
                face_names, face_locations = self._find_faces(frame, known_face_names, known_face_encodings)

                self._highlight_faces(frame, face_names, face_locations)

                if self.show:
                    cv2.imshow('frame', frame)
                    cv2.waitKey(1)

                writer.write(frame)

    def _find_faces(self, frame, known_face_names, known_face_encodings):

        frame = cv2.resize(frame, (0, 0), fx=self.frame_scale, fy=self.frame_scale)

        rgb_frame = frame[:, :, ::-1]
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = None

            # If a match was found in known_face_encodings, just use the first one.
            if True in matches:
                first_match_index = matches.index(True)
                name = known_face_names[first_match_index]

            face_names.append(name)

        if self.highlight_faces:
            face_locations = [(int(c / self.frame_scale) for c in coordinates) for coordinates in face_locations]

        return face_names, face_locations

    def _highlight_faces(self, frame, face_names, face_locations):
        font = cv2.FONT_HERSHEY_SIMPLEX
        FONT_SCALE = 0.5
        TEXT_PADDING = 6
        if self.highlight_faces:
            for (top, right, bottom, left), name in zip(face_locations, face_names):
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

                name = name or 'Unknown'
                text_size = cv2.getTextSize(name, font, FONT_SCALE, 1)[0]
                name_box_height = text_size[1] + TEXT_PADDING * 2
                left_padding = (right - left) // 2 - text_size[0] // 2
                cv2.rectangle(frame, (left, bottom - name_box_height), (right, bottom), (0, 255, 0), cv2.FILLED)
                cv2.putText(frame, name, (left + left_padding, bottom - TEXT_PADDING), font, FONT_SCALE,
                            (255, 255, 255), 1)
        else:
            # Show only names
            names = list(filter(lambda n: n is not None, face_names))

            unknowns_count = face_names.count(None)
            if unknowns_count:
                names.append(f'{unknowns_count} unknown')

            names_string = ', '.join(names)
            text_size = cv2.getTextSize(names_string, font, FONT_SCALE, 1)[0]

            textX = (frame.shape[1] - text_size[0]) // 2
            textY = (frame.shape[0] - 10)

            # add text centered on image
            cv2.putText(frame, names_string, (textX, textY), font, FONT_SCALE, (255, 255, 255), 1)

    @staticmethod
    def _encode_cast_photos(cast_photos):
        log.i('Encoding cast faces ...')

        known_face_names = []
        known_face_encodings = []

        total_photos = sum(len(photos) for photos in cast_photos.values())
        pbar = tqdm(desc='Encoding', total=total_photos, unit='photo', bar_format=PB_FMT)

        for name, photos in cast_photos.items():
            log.v(f'Encoding {name} photos:', pbar=pbar)
            for photo in photos:
                image = face_recognition.load_image_file(photo)
                try:
                    known_face_encodings.append(face_recognition.face_encodings(image)[0])
                    known_face_names.append(name)
                    log.v(f'\t{photo} encoded', pbar=pbar)
                except IndexError:
                    log.v(f'\t Failed to encode {photo}. Face not found.', pbar=pbar)

                pbar.update()
        log.i('Finished encoding.')
        return known_face_names, known_face_encodings
