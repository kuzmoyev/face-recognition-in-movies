# Face recognition in movies

Face recognition application.

* [Report](https://gitlab.fit.cvut.cz/kuzmoyev/mvi-sp/blob/master/report/report.pdf) 
* [Sources](https://gitlab.fit.cvut.cz/kuzmoyev/mvi-sp/tree/master/src)

## Task

Implement console application for recognition of actors' faces in the movies.
Analyse methods of face recognition in [face_recognition](https://github.com/ageitgey/face_recognition)
library. Application will primarily use [IMDB actors faces dataset](https://data.vision.ee.ethz.ch/cvl/rrothe/imdb-wiki/)
and [TMDB API](https://www.themoviedb.org/documentation/api?language=en) for retrieving actors faces and movie casts.

Output of the application will be:
 * copy of the input video with highlighted and named faces
 * actors' appearances throughout the movie in csv format
 * visualization of actors appearances throughout the movie

Report will also containe a description of the algorithms and methods used in face_recognition library.

## Installation

#### Requires

* Python3.6
* virtualenv

#### Setup

    git clone git@gitlab.fit.cvut.cz:kuzmoyev/mvi-sp.git FaceRecognition
    cd FaceRecognition
    virtualenv -p /usr/bin/python3.6 venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd src


#### Ask for help

    ./movie_face_recognition.py --help

#### Quick test

Following command will run analysis on Reservoir Dogs trailer. It will download casts 
photos to `imdb/imdb_data/tmdb_images`. 
    
    ./movie_face_recognition.py "test_data/Reservoir Dogs.mp4" -fd

Should run at ~10 fps. It analysis 4 out of 20 frames per second (every 5th frame) hence
those jumps.