#!/usr/bin/env python

import argparse
import logging
import os

from processing.face_recognition import FaceRecognizer
from visualization.visualization import Visualizer
from imdb import imdb


def parse_args():
    examples = '''examples:

     ./%(prog)s "Pulp Fiction.mp4" -d                         # Analyze given video and display with list of actors in the frame
     ./%(prog)s "Pulp Fiction.mp4" -df                        # Highlight faces
     ./%(prog)s "video.mp4" -t "pulp fiction" -df             # With cast from Pulp Fiction
     ./%(prog)s "Pulp Fiction.mp4" -dfv                       # With detailed output
     ./%(prog)s "Pulp Fiction.mp4" -o "Analyzed.avi"          # Save result in "Analyzed.avi"
     ./%(prog)s "Pulp Fiction.mp4" -a "Bob" "bobs_photo.jpg"  # Also search for "Bob" from "bobs_photo.jpg"
     ./%(prog)s "Pulp Fiction.mp4" -s "stats.csv"             # Output analyzed data in csv format to "stats.csv"
     
     ./%(prog)s "Pulp Fiction.mp4" -t "pulp fiction" -dfv -a "Bob" "bobs_photo.jpg" -s "stats.csv" -o "Analyzed.avi"
     '''

    parser = argparse.ArgumentParser(description='Face recognition application.',
                                     usage='./%(prog)s FILE_NAME',
                                     epilog=examples,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('FILE_NAME', help='video file path or device id.')
    parser.add_argument('-v', '--verbose', help='detailed verbose output', required=False, action='store_true')
    parser.add_argument('-d', '--display', help='display output frames', required=False, action='store_true')
    parser.add_argument('-f', '--faces', help='highlight found faces', required=False, action='store_true')

    parser.add_argument('-t', '--title', help='title of the movie (used for the specification of the cast). '
                                              'If not specified, will use input file name '
                                              'as a title (without extension).', required=False)
    parser.add_argument('-o', '--output', help='output video file with recognised faces', required=False,
                        metavar='PATH')
    parser.add_argument('-s', '--stats', help='output stats file path', required=False, metavar='PATH')
    parser.add_argument('-p', '--plot', help='output visualization image path', required=False,
                        metavar='PATH')
    parser.add_argument('-n', '--actors-to-plot', help='number of top actors to plot in visualization (default - 5)',
                        required=False, metavar='PATH', default=5, type=int)
    parser.add_argument('-a', '--additional-photos', help='additional photos', default=[],
                        required=False, nargs=argparse.ONE_OR_MORE, action='append', metavar=('NAME PATH', 'PATH'))

    args = parser.parse_args()

    if any(len(l) < 2 for l in args.additional_photos):
        print('Parameter -a/--additional-photos requires at least 2 arguments.')
        print('usage: ./movie_face_recognition.py FILE_NAME -a NAME PATH [PATH ...]')
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

    try:
        # check if input is a device
        input_video = int(args.FILE_NAME)
        movie_title = args.title
    except ValueError:
        # input from file
        input_video = args.FILE_NAME
        movie_title = args.title or os.path.splitext(os.path.basename(input_video))[0]  # cut extension

    output_video = args.output
    display_frames = args.display
    highlight_faces = args.faces
    stats_file = args.stats
    plot_path = args.plot

    cast = imdb.get_cast_images(movie_title) if movie_title else {}
    for name, *paths in args.additional_photos:
        cast[name] = paths

    face_recognizer = FaceRecognizer(display=display_frames, highlight_faces=highlight_faces)
    stats, movie_length = face_recognizer.process(input_video, cast, output_video, stats_file=stats_file)


    if plot_path:
        visualizer = Visualizer()
        visualizer.save_plot(plot_path, stats, movie_length, top_actors_count=args.actors_to_plot)


if __name__ == '__main__':
    main()
