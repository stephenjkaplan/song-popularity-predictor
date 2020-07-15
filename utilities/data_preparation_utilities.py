"""
Contains utility functions necessary to process and transform data before modeling steps.
Author: Stephen Kaplan (July 11, 2020)
"""
import pandas as pd


def generate_spotify_album_features(album_tracks):
    """

    :param album_tracks: note that it shouldnt contain index
    :return:
    """
    album_name = album_tracks['Album Title'].iloc[0]
    artist = album_tracks['Artist'].iloc[0]
    num_tracks = len(album_tracks)
    duration_minutes = round(album_tracks['Duration (ms)'].sum()/1000/60, 2)
    avg_tempo = round(album_tracks['Tempo'].mean(), 2)
    majorness = round(album_tracks['Mode'].sum() / len(album_tracks), 4)
    avg_danceability = round(album_tracks['Danceability'].mean(), 4)
    avg_energy = round(album_tracks['Energy'].mean(), 4)
    avg_loudness = round(album_tracks['Loudness'].mean(), 2)
    avg_speechiness = round(album_tracks['Speechiness'].mean(), 4)
    avg_acousticness = round(album_tracks['Acousticness'].mean(), 4)
    avg_instrumentalness = round(album_tracks['Instrumentalness'].mean(), 4)
    avg_liveness = round(album_tracks['Liveness'].mean(), 4)
    avg_valence = round(album_tracks['Valence'].mean(), 4)

    return pd.DataFrame({
        'Album Title': [album_name],
        'Artist': [artist],
        'Number of Tracks': [num_tracks],
        'Duration (minutes)': [duration_minutes],
        'Avg Tempo': [avg_tempo],
        'Majorness': [majorness],
        'Avg Danceability': [avg_danceability],
        'Avg Energy': [avg_energy],
        'Avg Loudness': [avg_loudness],
        'Avg Speechiness': [avg_speechiness],
        'Avg Acousticness': [avg_acousticness],
        'Avg Instrumentalness': [avg_instrumentalness],
        'Avg Liveness': [avg_liveness],
        'Avg Valence': [avg_valence]
    })
