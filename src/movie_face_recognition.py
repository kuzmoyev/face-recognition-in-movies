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

    return parser.parse_args()


def init_logger(verbose):
    VERBOSE_LEVEL = 15

    def _verbose(self, message, *args, **kws):
        if self.isEnabledFor(VERBOSE_LEVEL):
            self._log(VERBOSE_LEVEL, message, args, **kws)

    logging.Logger.v = _verbose
    logging.Logger.i = logging.Logger.info

    logging.basicConfig(format='%(message)s', datefmt='%H:%M:%S', level=VERBOSE_LEVEL if verbose else logging.INFO)


if __name__ == '__main__':
    args = parse_args()
    init_logger(args.verbose)

    input_video = args.FILE_NAME
    output_video = args.output
    movie_title = args.MOVIE_TITLE
    show_frames = args.show
    highlight_faces = args.faces

    cast = imdb.get_cast_images(movie_title)

    face_recognizer = FaceRecognizer(show=show_frames, highlight_faces=highlight_faces)
    face_recognizer.process(input_video, cast, output_video)
