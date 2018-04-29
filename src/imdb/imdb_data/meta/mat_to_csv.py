import scipy.io
import pandas as pd
import numpy as np

data = scipy.io.loadmat("imdb.mat")

data = data['imdb']

mdtype = data.dtype
needed_columns = ['photo_taken', 'full_path', 'name', 'celeb_id', 'face_score', 'second_face_score']
ndata = {n: data[n][0][0] for n in mdtype.names if n in needed_columns}
columns = [n for n, v in ndata.items()]

ndata['name'] = np.array([s[0] for s in ndata['name'][0]], dtype=np.str)

ndata['celeb_id'] = ndata['celeb_id'][0]

ndata['full_path'] = np.array([s[0] for s in ndata['full_path'][0]], dtype=np.str)

ndata['photo_taken'] = ndata['photo_taken'][0]

ndata['face_score'] = ndata['face_score'][0]

ndata['second_face_score'] = ndata['second_face_score'][0]

index = ndata['celeb_id']
ndata.pop('celeb_id')

df = pd.DataFrame(ndata, index=index)

df = df[(df['second_face_score'].isnull()) & (df['face_score'] > 0)].drop(['second_face_score'], axis=1)

df = df.rename({'face_score': 'score', 'full_path': 'path', 'photo_taken': 'year'}, axis=1)

df['name'] = df['name'].str.lower()

df.to_csv('imdb.csv')
