import requests
import urllib.request
import json
import pandas as pd
import os

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
DATA_FOLDER = '/home/imdb_data'
METADATA_FOLDER = os.path.join(DATA_FOLDER, 'meta')
IMDB_IMAGES_FOLDER = os.path.join(DATA_FOLDER, 'imdb_images')
IMDB_METADATA = os.path.join(METADATA_FOLDER, 'imdb.csv')
TMDB_IMAGES_FOLDER = os.path.join(DATA_FOLDER, 'tmdb_images')
TMDB_METADATA = os.path.join(METADATA_FOLDER, 'tmdb.csv')


def get_movie_data(title):
    found_data = requests.get(SEARCH_MOVIES_URL.format(title)).text
    data = json.loads(found_data)
    movie_id = data['results'][0]['id']
    credits_data = requests.get(MOVIE_DETAILS_URL.format(movie_id)).text
    return json.loads(credits_data)


def download_image(image_name, image_path):
    url = IMG_URL.format(image_name)
    urllib.request.urlretrieve(url, image_path)


def get_cast_images(movie, count=5, year_delta=3):
    data = get_movie_data(movie)
    year = int(data['release_date'].split('-')[0])

    imdb_df = pd.read_csv(IMDB_METADATA)
    imdb_df = imdb_df[imdb_df['year'].between(year - year_delta, year + year_delta)]

    try:
        tmdb_df = pd.read_csv(TMDB_METADATA)
    except FileNotFoundError:
        tmdb_df = pd.DataFrame(columns=['name', 'path'])

    res = {}

    for actor_data in data['credits']['cast']:
        name = actor_data['name'].lower()

        relevant_images = imdb_df[imdb_df['name'] == name]
        relevant_images = relevant_images.sort_values(['score'], ascending=False)

        if relevant_images.empty:
            # Getting from TMDB data
            tmdb_image = tmdb_df[tmdb_df['name'] == name]
            tmdb_image_path = actor_data['profile_path']

            if not tmdb_image_path:
                # No image in TMDB
                continue

            image_name = tmdb_image_path.replace('/', '')
            image_path = os.path.join(TMDB_IMAGES_FOLDER, image_name)

            if not os.path.exists(image_path):
                print('Downloading', name)
                download_image(image_name, image_path)
            if tmdb_image.empty:
                tmdb_df = tmdb_df.append({'name': name, 'path': image_path}, ignore_index=True)

            res[name] = [image_path]
        else:
            # Getting from IMDB data
            res[name] = [os.path.join(IMDB_IMAGES_FOLDER, p) for p in relevant_images['path'][:count]]

    tmdb_df.to_csv(TMDB_METADATA, index=False)
    return res


if __name__ == '__main__':
    print(get_cast_images('Pulp fiction', count=1))
