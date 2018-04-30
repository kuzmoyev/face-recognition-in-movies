import datetime

from video_wrappers.video_wrappers import VideoReader, VideoWriter

import cv2
import face_recognition
import pandas as pd
import numpy as np

from tqdm import tqdm
import logging

log = logging.getLogger()

PB_L = '{desc}: {percentage:3.02f}%'
PB_B = ' |{bar}| '
PB_R = '{n_fmt}/{total_fmt}{postfix} [passed - {elapsed} | left ~ {remaining} | {rate_fmt}]'
PB_FMT = PB_L + PB_B + PB_R


class FaceRecognizer:
    def __init__(self,
                 display=True,
                 highlight_faces=False,
                 analyzed_height=480,
                 analyzed_fps=4
                 ):

        self.display = display
        self.highlight_faces = highlight_faces
        self.analyzed_height = analyzed_height
        self.analyzed_fps = analyzed_fps

    def process(self, input_video, cast_photos, output_video=None, stats_file=None):
        log.i('Starting processing.')

        known_face_names, known_face_encodings = self._encode_cast_photos(cast_photos)

        face_names = []
        face_locations = []
        if stats_file:
            stats_df = pd.DataFrame(columns=['frame', 'Unknown'] + list(cast_photos.keys()))
        else:
            stats_df = None

        with VideoReader(input_video) as reader, VideoWriter(output_video, **reader.parameters) as writer:
            analyzed_frame = reader.fps // self.analyzed_fps
            frames = reader.frames(return_frame_count=True)
            total_frames = reader.frames_count
            frame_scale = min(self.analyzed_height / reader.height, 1)

            log.v(f'Analysis info:')
            log.v(f'\tAnalyzing every {analyzed_frame} frame.')
            log.v(f'\tFrame resize factor is {frame_scale:.2f}.')
            log.v(f'\tOriginal frame size {reader.width}x{reader.height}.')
            log.v(f'\tAnalyzed frame size {reader.width*frame_scale:.0f}x{reader.height*frame_scale:.0f}.')

            pbar = tqdm(frames, desc='Progress', total=total_frames, unit='frame', bar_format=PB_FMT)
            for f, frame in pbar:
                if f % analyzed_frame == 0:
                    small_frame = cv2.resize(frame, (0, 0), fx=frame_scale, fy=frame_scale)
                    face_names, face_locations = self._find_faces(small_frame, known_face_names, known_face_encodings)
                    face_locations = [[int(c / frame_scale) for c in coordinates] for coordinates in face_locations]

                    if stats_file:
                        stats_df = self._append_to_stats(stats_df, f, face_names, face_locations)

                if self.display or writer.active():
                    self._highlight_faces(frame, face_names, face_locations)

                    if self.display:
                        cv2.imshow('frame', frame)
                        cv2.waitKey(1)

                    if writer.active():
                        writer.write(frame)

                current_position = datetime.timedelta(seconds=reader.current_position)
                movie_length = datetime.timedelta(seconds=reader.video_length) if reader.video_length else '∞'
                pbar.set_postfix({'time': f"{current_position}s/{movie_length}s"})
        if stats_file:
            stats_df.to_csv(stats_file)

    @staticmethod
    def _append_to_stats(df, frame, face_names, face_locations):
        row = dict(zip(df.columns, [None] * len(df.columns)))
        row['frame'] = frame

        for name, location in zip(face_names, face_locations):
            row[name or 'Unknown'] = np.array(location)

        return df.append(row, ignore_index=True)

    def _find_faces(self, frame, known_face_names, known_face_encodings):
        rgb_frame = frame[:, :, ::-1]
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = None

            # If a match was found in known_face_encodings, just use the first one.
            if any(matches):
                first_match_index = matches.index(True)
                name = known_face_names[first_match_index]

            face_names.append(name)

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
                cv2.rectangle(frame, (left, bottom), (right, bottom + name_box_height), (0, 255, 0), cv2.FILLED)
                cv2.putText(frame, name, (left + left_padding, bottom + text_size[1] + TEXT_PADDING), font, FONT_SCALE,
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

        return known_face_names, known_face_encodings
