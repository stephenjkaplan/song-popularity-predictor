"""
Contains utility functions necessary to scrape pitchfork album rating data and Spotify audio feature data.
Author: Stephen Kaplan (July 8, 2020)
"""
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from spotipy.client import SpotifyException


def scroll_infinite_page(driver, num_albums_per_genre, scroll_pause=1.0):
    """

    :param driver:
    :param num_albums_per_genre:
    :param scroll_pause:
    :return:
    """
    # scroll on the page a large amount of times until number of desired album records are visible on page
    for i in range(1000):
        num_review_collections = len(driver.find_elements_by_class_name('review-collection-fragment'))
        # there are 12 album records per review collection. check if total album records is sufficient
        if num_review_collections*12 >= num_albums_per_genre:
            break
        else:
            # scroll down to bottom and wait to load page
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause)


def get_album_rating(url, genre):
    """

    :param url:
    :param genre:
    :return:
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # parse and extract desired album review data
    artist = soup.find('ul', attrs={'class': 'artist-links'}).find('a').text
    album_title = soup.find('h1', attrs={'class': 'single-album-tombstone__review-title'}).text
    album_rating = float(soup.find('span', attrs={'class': 'score'}).text)

    return {'Artist': artist, 'Album Title': album_title, 'Genre': genre, 'Rating': album_rating}


def get_album_review_urls(driver, num_albums_per_genre):
    """

    :param driver:
    :param num_albums_per_genre:
    :return:
    """
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    reviews = soup.find_all('a', {'class': 'review__link'})
    urls = [f"https://pitchfork.com{review.get('href')}" for review in reviews]

    return urls[0:num_albums_per_genre]


def get_pitchfork_album_ratings_for_genre(driver, genre, num_albums_per_genre):
    """

    :return:
    """
    print(f'Scraping Pitchfork album ratings for {genre} genre...')

    # compose full URL that will filter album ratings page to a single genre, and navigate to URL
    base_url = 'https://pitchfork.com/reviews/albums/'
    genre_lower = genre.lower().split('/')[0]       # somewhat different format in URL than web page
    driver.get(url=f'{base_url}?genre={genre_lower}')

    # scroll down infinite scrolling page enough times to display number of records requested.
    scroll_infinite_page(driver, num_albums_per_genre)

    urls = get_album_review_urls(driver, num_albums_per_genre)
    album_ratings = [get_album_rating(url, genre) for url in urls]
    df_album_ratings_genre = pd.DataFrame(album_ratings)

    return df_album_ratings_genre


def get_pitchfork_album_ratings(driver, genres, num_albums_per_genre):
    """

    :param driver:
    :param int num_albums_per_genre:
    :param list genres:
    :return:
    :rtype:
    """
    genre_dataframes = [get_pitchfork_album_ratings_for_genre(driver, genre, num_albums_per_genre) for genre in genres]
    driver.quit()   # close Chrome window

    return pd.concat(genre_dataframes)


def get_spotify_album(spotify_api_client, album_name, artist_name):
    """

    :param spotify_api_client:
    :param album_name:
    :param artist_name:
    :return:
    """
    query = f'album:{album_name} artist:{artist_name}'
    response = spotify_api_client.search(q=query, type='album')
    album_results = response['albums']['items']
    if not album_results:
        print(f'Unable to find {album_name} by {artist_name} on Spotify...')
        return None
    else:
        album = album_results[0]
        return album


def get_spotify_track_audio_features_for_album(spotify_api_client, album_uri):
    """

    :param spotify_api_client:
    :param album_uri:
    :return:
    """
    album_tracks = spotify_api_client.album_tracks(album_uri)['items']
    album_track_uris = [track['uri'] for track in album_tracks]
    track_audio_features = spotify_api_client.audio_features(tracks=album_track_uris)

    return track_audio_features


def format_album_names_for_spotify(album_names):
    """

    :param album_names:
    :return:
    """
    # remove "EP" suffix from albums that are EP's
    album_names = [a.replace(' EP', '') for a in album_names]

    return album_names


def get_spotify_track_audio_features(spotify_api_client, album_names, artist_names):
    """
    searches

    :param spotify_api_client:
    :param album_names:
    :param artist_names:
    :return:
    """
    album_names_spotify = format_album_names_for_spotify(album_names)

    track_audio_features = []
    for album_name, artist_name in zip(album_names_spotify, artist_names):
        try:
            album = get_spotify_album(spotify_api_client, album_name, artist_name)
            if album is None:
                continue
            else:
                track_audio_features_album= get_spotify_track_audio_features_for_album(spotify_api_client, album['uri'])
                track_audio_features.extend({
                    'Track URI': track['uri'],
                    'Album Title': album_name,
                    'Artist': artist_name,
                    'Duration (ms)': track['duration_ms'],
                    'Tempo': track['tempo'],
                    'Key': track['key'],
                    'Mode': track['mode'],
                    'Time Signature': track['time_signature'],
                    'Danceability': track['danceability'],
                    'Energy': track['energy'],
                    'Loudness': track['loudness'],
                    'Speechiness': track['speechiness'],
                    'Acousticness': track['acousticness'],
                    'Instrumentalness': track['instrumentalness'],
                    'Liveness': track['liveness'],
                    'Valence': track['valence']
                } for track in track_audio_features_album)

        except (SpotifyException, TypeError):
            print(f'Spotify Error for {album_name} by {artist_name}...')

    # convert to DataFrame and reorder columns
    df_track_audio_features = pd.DataFrame(track_audio_features)
    df_track_audio_features = df_track_audio_features[['Track URI', 'Album Title', 'Artist', 'Duration (ms)', 'Tempo',
                                                       'Key', 'Mode', 'Time Signature', 'Danceability', 'Energy',
                                                       'Loudness', 'Speechiness', 'Acousticness', 'Instrumentalness',
                                                       'Liveness', 'Valence']]

    return df_track_audio_features


def get_spotify_track_popularity_and_artist_followers(spotify_api_client, track_uris):
    """

    :param spotify_api_client:
    :param track_uris:
    :return:
    """
    # break track URI list into groups of 50 (since endpoint can only handle 50 at a time)
    group_size = 50
    track_uri_groups = zip(*(iter(track_uris),) * group_size)

    # for each grouping, pull tracks, get popularity, and append to list
    track_popularity = []
    for track_uri_group in track_uri_groups:
        response = spotify_api_client.tracks(tracks=list(track_uri_group))
        tracks = response['tracks']

        artist_uris = [track['artists'][0]['uri'] for track in tracks]
        artists = spotify_api_client.artists(artist_uris)['artists']

        track_popularity.extend([{
            'Track URI': track['uri'],
            'Popularity': track['popularity'],
            'Artist Followers': artist['followers']['total']
        } for track, artist in zip(tracks, artists)])

    df_spotify_track_popularity = pd.DataFrame(track_popularity)

    return df_spotify_track_popularity


def replace_track_features_with_correct_album(spotify_api_client, album_name, artist_name, correct_album_uri,
                                              df_spotify):
    """

    :param spotify_api_client:
    :param album_name:
    :param artist_name:
    :param correct_album_uri:
    :param df_spotify:
    :return:
    """
    # get correct track features and convert to pandas DataFrame
    correct_track_features = get_spotify_track_audio_features_for_album(spotify_api_client, correct_album_uri)
    df_correct_track_features = pd.DataFrame([{
        'Track URI': track['uri'],
        'Album Title': album_name,
        'Artist': artist_name,
        'Duration (ms)': track['duration_ms'],
        'Tempo': track['tempo'],
        'Key': track['key'],
        'Mode': track['mode'],
        'Time Signature': track['time_signature'],
        'Danceability': track['danceability'],
        'Energy': track['energy'],
        'Loudness': track['loudness'],
        'Speechiness': track['speechiness'],
        'Acousticness': track['acousticness'],
        'Instrumentalness': track['instrumentalness'],
        'Liveness': track['liveness'],
        'Valence': track['valence']
    } for track in correct_track_features])

    # filter out existing data with that
    df_spotify_corrected = df_spotify[df_spotify['Album Title'] != album_name]
    df_spotify_corrected = df_spotify_corrected.append(df_correct_track_features)

    return df_spotify_corrected
