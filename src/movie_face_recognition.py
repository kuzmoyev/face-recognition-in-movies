#!/usr/bin/env python

import argparse
import logging

from processing.face_recognition import FaceRecognizer
from imdb import imdb


def parse_args():
    parser = argparse.ArgumentParser(description='Face recognition application.',
                                     usage='%(prog)s FILE_NAME MOVIE_TITLE')

    parser.add_argument('FILE_NAME', help='video file path')
    parser.add_argument('MOVIE_TITLE', help='title of the movie (used for the specification of the cast)')

    parser.add_argument('-o', '--output', help='output video file with recognised faces', required=False, metavar='F')
    parser.add_argument('-v', '--verbose', help='detailed verbose output', required=False, action='store_true')
    parser.add_argument('-s', '--show', help='show output frames', required=False, action='store_true')
    parser.add_argument('-f', '--faces', help='highlight found faces', required=False, action='store_true')
    parser.add_argument('-a', '--additional-photos', help='additional photos',
                        required=False, nargs=argparse.ONE_OR_MORE, action='append', metavar=('NAME PATH', 'PATH'))

    args = parser.parse_args()

    if any(len(l) < 2 for l in args.additional_photos):
        print('Parameter -a/--additional-photos requires at least 2 arguments.')
        print('usage: movie_face_recognition.py FILE_NAME MOVIE_TITLE -a NAME PATH [PATH ...]')
        exit()

    return args


def init_logger(verbose):
    VERBOSE_LEVEL = 15

    def _verbose(self, message, pbar=None, *args, **kwargs):
        if self.isEnabledFor(VERBOSE_LEVEL):
            if pbar:
                pbar.write(message)
            else:
                self._log(VERBOSE_LEVEL, message, args, **kwargs)

    def _info(self, message, pbar=None, *args, **kwargs):
        if self.isEnabledFor(logging.INFO):
            if pbar:
                pbar.write(message)
            else:
                self._log(logging.INFO, message, args, **kwargs)

    logging.Logger.v = _verbose
    logging.Logger.i = _info

    logging.basicConfig(format='%(message)s', datefmt='%H:%M:%S', level=VERBOSE_LEVEL if verbose else logging.INFO)


def main():
    args = parse_args()
    init_logger(args.verbose)

    input_video = args.FILE_NAME if args.FILE_NAME != '0' else 0
    output_video = args.output
    movie_title = args.MOVIE_TITLE
    show_frames = args.show
    highlight_faces = args.faces

    print(args)

    cast = imdb.get_cast_images(movie_title)

    for name, *paths in args.additional_photos:
        cast[name] = paths

    face_recognizer = FaceRecognizer(show=show_frames, highlight_faces=highlight_faces)
    face_recognizer.process(input_video, cast, output_video)


if __name__ == '__main__':
    main()
