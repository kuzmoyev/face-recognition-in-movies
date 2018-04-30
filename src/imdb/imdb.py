import requests
import urllib.request
import json
import pandas as pd
import os

import logging

log = logging.getLogger()

############### TMDB API ###############
API_KEY = "4596b584a16d4343841d1ec382424eff"
API_KEY_PARAMETER = "api_key=" + API_KEY
API_URL = "https://api.themoviedb.org/3"
IMG_URL = "https://image.tmdb.org/t/p/original/{}"

SEARCH_MOVIES_PARAMETER = "/search/movie?query={}"
MOVIE_DETAILS_PARAMETER = "/movie/{}"
CREDITS_PARAMETER = "append_to_response=credits"

SEARCH_MOVIES_URL = API_URL + SEARCH_MOVIES_PARAMETER + '&' + API_KEY_PARAMETER
MOVIE_DETAILS_URL = API_URL + MOVIE_DETAILS_PARAMETER + '?' + CREDITS_PARAMETER + '&' + API_KEY_PARAMETER

############### IMAGES ###############
# if IMDB dataset is used (https://data.vision.ee.ethz.ch/cvl/rrothe/imdb-wiki/)
BIG_DATA_FOLDER = '/home/imdb_data'

# if IMDB dataset is not used. All photos will be downloaded from TMDB.
SMALL_DATA_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'imdb_data')

DATA_FOLDER = BIG_DATA_FOLDER if os.path.exists(BIG_DATA_FOLDER) else SMALL_DATA_FOLDER
METADATA_FOLDER = os.path.join(DATA_FOLDER, 'meta')
IMDB_IMAGES_FOLDER = os.path.join(DATA_FOLDER, 'imdb_images')
IMDB_METADATA = os.path.join(METADATA_FOLDER, 'imdb.csv')
TMDB_IMAGES_FOLDER = os.path.join(DATA_FOLDER, 'tmdb_images')
TMDB_METADATA = os.path.join(METADATA_FOLDER, 'tmdb.csv')

# Ensure data folders
for directory in DATA_FOLDER, METADATA_FOLDER, IMDB_IMAGES_FOLDER, TMDB_IMAGES_FOLDER:
    if not os.path.exists(directory):
        os.makedirs(directory)


def get_movie_data(title):
    found_data = requests.get(SEARCH_MOVIES_URL.format(title)).text
    data = json.loads(found_data)
    try:
        movie_id = data['results'][0]['id']
        credits_data = requests.get(MOVIE_DETAILS_URL.format(movie_id)).text
    except IndexError:
        log.error(f"Movie {title} not found.")
        raise

    return json.loads(credits_data)


def download_image(image_name, image_path):
    url = IMG_URL.format(image_name)
    urllib.request.urlretrieve(url, image_path)


def get_cast_images(movie, max_actors=20, max_images_per_actor=3, year_delta=3):
    """Get names and images of actors.

    :param movie: movie title (used as a search query).
    :param max_actors: limit of actors. 0 - for the whole cast.
    :param max_images_per_actor: number of images per actor.
                                 If no images in IMDB database, one image returned (from TMDB).
                                 If no image in TMDB either, actor will not be returned in the result.
    :param year_delta: filter photos taken between (release_year - year_delta) and (release_year + year_delta)

    :return: dictionary {actor_name: [photo_path, photo_path, ...]}
    """

    try:
        data = get_movie_data(movie)
    except IndexError:
        return {}

    release_year = int(data['release_date'].split('-')[0])

    max_actors = max_actors or len(data["credits"]["cast"])

    directors = [d['name'] for d in data["credits"]["crew"] if d['job'] == 'Director']
    log.i(f'Searching cast for "{data["original_title"]}" ...')
    log.v('Movie data:')
    log.v(f'\tTitle: {data["original_title"]}')
    log.v(f'\tRelease: {data["release_date"]}')
    log.v(f'\tRuntime: {data["runtime"]}s')
    log.v(f'\tCredited actors number: {len(data["credits"]["cast"])} ({max_actors} will be used)')
    log.v(f'\tDirector(s): {", ".join(directors)}')

    imdb_df = pd.read_csv(IMDB_METADATA)
    imdb_df = imdb_df[imdb_df['year'].between(release_year - year_delta, release_year + year_delta)]

    try:
        tmdb_df = pd.read_csv(TMDB_METADATA)
    except FileNotFoundError:
        tmdb_df = pd.DataFrame(columns=['name', 'path'])

    res = {}

    found_locally = 0
    downloaded = 0
    log.v('Cast:')
    for actor_data in data['credits']['cast'][:max_actors]:
        name = actor_data['name']
        name_lower = name.lower()

        relevant_images = imdb_df[imdb_df['name'] == name_lower]
        relevant_images = relevant_images.sort_values(['score'], ascending=False)

        if relevant_images.empty:
            # Getting from TMDB data
            tmdb_image = tmdb_df[tmdb_df['name'] == name_lower]
            tmdb_image_path = actor_data['profile_path']

            if not tmdb_image_path:
                # No image in TMDB
                continue

            image_name = tmdb_image_path.replace('/', '')
            image_path = os.path.join(TMDB_IMAGES_FOLDER, image_name)

            if not os.path.exists(image_path):
                download_image(image_name, image_path)
                downloaded += 1
                log.v(f'\t{name}: downloaded - [{image_path}]')
            else:
                found_locally += 1
                log.v(f'\t{name}: local - [{image_path}]')
            if tmdb_image.empty:
                tmdb_df = tmdb_df.append({'name': name_lower, 'path': image_path}, ignore_index=True)

            res[name] = [image_path]
        else:
            # Getting from IMDB data
            actor_photos = [os.path.join(IMDB_IMAGES_FOLDER, p) for p in relevant_images['path'][:max_images_per_actor]]
            res[name] = actor_photos
            found_locally += len(actor_photos)
            if len(actor_photos) > 1:
                log.v(f'\t{name}: local - [{actor_photos[0]}, ... {len(actor_photos) - 1} more]')
            else:
                log.v(f'\t{name}: local - [{actor_photos[0]}]')

    tmdb_df.to_csv(TMDB_METADATA, index=False)

    log.i(f'For {max_actors} actors, {found_locally} photos found locally, {downloaded} photos downloaded.')
    return res


if __name__ == '__main__':
    print(get_cast_images('Pulp fiction', max_images_per_actor=1))
