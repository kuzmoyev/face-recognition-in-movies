import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

from matplotlib import colors as mcolors

import datetime
import time
import os
import datetime


def sec_to_time(s):
    return str(datetime.timedelta(seconds=int(s)))


def time_to_sec(t):
    x = time.strptime(t, '%H:%M:%S')
    return datetime.timedelta(hours=x.tm_hour, minutes=x.tm_min, seconds=x.tm_sec).total_seconds()


class Visualizer:
    def save_plot(self, path, df, movie_length, top_actors_count=5, events=None):
        fps = df['frame'].max() / movie_length
        df['second'] = df['frame'] // fps
        df.drop('Unnamed: 0', axis=1, errors='ignore', inplace=True)

        events = events or {}
        seconds_window = movie_length // 160 + 1
        min_frames = seconds_window // 3

        app_df = df.drop('frame', axis=1).notnull().astype(np.uint8)
        app_df['second'] = df['second']
        app_df = app_df.groupby(app_df['second'] // seconds_window * seconds_window).sum()
        top_actors = app_df.drop(['Unknown', 'second'], axis=1).sum(axis=0).nlargest(top_actors_count).index

        app_df = app_df[top_actors]

        fig, ax = plt.subplots(figsize=(12, 5))

        for i, ((name, col), c) in enumerate(zip(app_df.items(), mcolors.BASE_COLORS)):
            for n, (start, app) in enumerate(col.iloc[:-1].iteritems()):
                finish = col.index[n + 1]
                if app > min_frames:
                    ax.broken_barh([[start, finish - start]], (i - 0.4, 0.8), color=c)

        s = app_df.shape[0]
        ax.set_yticks(range(len(app_df.columns)))
        ax.set_yticklabels(app_df.columns)
        ax.set_xticks(app_df.index[::s // 10])
        ax.set_xticklabels(sec_to_time(sec) for sec in app_df.index[::s // 10])

        bottom, top = ax.get_ybound()
        for t, e in events.items():
            plt.axvline(x=t, linestyle='--', color='grey')
            plt.text(x=t, y=top + (top - bottom) * 0.01, s=e)

        plt.savefig(path)
