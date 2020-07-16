"""
Contains utility functions necessary to scrape pitchfork album rating data and Spotify audio feature data, as well as
perform some transformations.
Author: Stephen Kaplan (July 8, 2020)
"""
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from spotipy.client import SpotifyException


def scroll_infinite_page(driver, num_albums, scroll_pause=1.0):
    """
    Uses a Selenium web driver to scroll down on an "infinitely scrolling page" on Pitchfork.com. This causes more
    album reviews to load on the page. Scrolls until it counts a sufficient number of album review elements on the
    HTML page.

    :param selenium.webdriver.chrome.webdriver.WebDriver driver: Selenium web driver
    :param int num_albums: The number of albums to pull Pitchfork reviews for.
    :param float scroll_pause: Time (seconds) to wait for page to load after scroll.
    """
    # scroll on the page a large amount of times until number of desired album records are visible on page
    for i in range(1000):
        num_review_collections = len(driver.find_elements_by_class_name('review-collection-fragment'))
        # there are 12 album records per review collection. check if total album records is sufficient
        if num_review_collections*12 >= num_albums:
            break
        else:
            # scroll down to bottom and wait to load page
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause)


def get_album_rating(url, genre):
    """
    Scrapes album rating and other useful metadata from a Pitchfork album review page.

    :param str url: Full link to a Pitchfork album rating.
    :param str genre: Genre of album, simply used to add to data record that is returned.
    :return: Dictionary containing album rating and useful metadata.
    :rtype: dict
    """
    # get raw HTML
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # parse and extract desired album review data
    artist = soup.find('ul', attrs={'class': 'artist-links'}).find('a').text
    album_title = soup.find('h1', attrs={'class': 'single-album-tombstone__review-title'}).text
    album_rating = float(soup.find('span', attrs={'class': 'score'}).text)

    return {'Artist': artist, 'Album Title': album_title, 'Genre': genre, 'Rating': album_rating}


def get_album_review_urls(driver, num_albums):
    """
    Gets links to specified number of album reviews.

    :param selenium.webdriver.chrome.webdriver.WebDriver driver: Selenium web driver
    :param int num_albums: The number of albums to pull Pitchfork reviews for.
    :return: URLs to album reviews
    :rtype: list
    """
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    reviews = soup.find_all('a', {'class': 'review__link'})
    urls = [f"https://pitchfork.com{review.get('href')}" for review in reviews]

    return urls[0:num_albums]


def get_pitchfork_album_ratings_for_genre(driver, genre, num_albums):
    """
    Gets Pitchfork album ratings and other useful metadata for a particular genre and number of albums.

    :param selenium.webdriver.chrome.webdriver.WebDriver driver: Selenium web driver
    :param str genre: Genre of music to get album reviews for. Must be one of: ['Electronic', 'Experimental',
                      'Folk/Country', 'Global', 'Jazz', 'Metal', 'Pop/R&B', 'Rap/Hip-Hop', 'Rock'].
    :param int num_albums: The number of albums to pull Pitchfork reviews for.
    :return: Pandas DataFrame containing Pitchfork album review data for a particular genre of music.
    :rtype: pandas.DataFrame
    """
    print(f'Scraping Pitchfork album ratings for {genre} genre...')

    # compose full URL that will filter album ratings page to a single genre, and navigate to URL
    base_url = 'https://pitchfork.com/reviews/albums/'
    genre_lower = genre.lower().split('/')[0]       # somewhat different format in URL than web page
    driver.get(url=f'{base_url}?genre={genre_lower}')

    # scroll down infinite scrolling page enough times to display number of records requested.
    scroll_infinite_page(driver, num_albums)

    urls = get_album_review_urls(driver, num_albums)
    album_ratings = [get_album_rating(url, genre) for url in urls]
    df_album_ratings_genre = pd.DataFrame(album_ratings)

    return df_album_ratings_genre


def get_pitchfork_album_ratings(driver, genres, num_albums_per_genre):
    """
    Gets Pitchfork album ratings and other useful metadata for a specified list of genres, and number of albums reviews
    per genre.

    :param selenium.webdriver.chrome.webdriver.WebDriver driver: Selenium web driver
    :param int num_albums_per_genre: The number of albums to pull Pitchfork reviews for each genre specified.
    :param list genres: List of genre of music to get album reviews for. Must consist of only the following:
                        ['Electronic', 'Experimental', 'Folk/Country', 'Global', 'Jazz', 'Metal', 'Pop/R&B',
                        'Rap/Hip-Hop', 'Rock'].
    :return: Pandas DataFrame containing Pitchfork album review data.
    :rtype: pandas.DataFrame
    """
    genre_dataframes = [get_pitchfork_album_ratings_for_genre(driver, genre, num_albums_per_genre) for genre in genres]
    driver.quit()   # close Chrome window

    return pd.concat(genre_dataframes)


def get_spotify_album(spotify_api_client, album_name, artist_name):
    """
    Search for Spotify album by album name and artist name and return result.

    :param object spotify_api_client: Client used to authenticate and make requests to Spotify's API.
    :param str album_name: Name of the album to search for.
    :param str artist_name: Artist of the album to search for.
    :return: Album data record from Spotify API.
    :rtype: dict
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
    Get data describing certain qualities of every track/song on a particular album hosted on Spotify.

    :param object spotify_api_client: Client used to authenticate and make requests to Spotify's API.
    :param str album_uri: Unique identifier associated with album on Spotify.
    :return: List of dictionaries containing track audio features.
    :rtype: list
    """
    album_tracks = spotify_api_client.album_tracks(album_uri)['items']
    album_track_uris = [track['uri'] for track in album_tracks]
    track_audio_features = spotify_api_client.audio_features(tracks=album_track_uris)

    return track_audio_features


def format_album_names_for_spotify(album_names):
    """
    Removes the "EP" tag from any album in a list of album names.

    :param list album_names: List of strings containing album names.
    :return: Formatted album names.
    :rtype: list
    """
    # remove "EP" suffix from albums that are EP's
    album_names = [a.replace(' EP', '') for a in album_names]

    return album_names


def get_spotify_track_audio_features(spotify_api_client, album_names, artist_names):
    """
    Gets data describing certain qualities of every track/song on a list of albums hosted on Spotify.

    :param object spotify_api_client: Client used to authenticate and make requests to Spotify's API.
    :param list album_names: Album names of the albums to acquire track audio feature data from.
    :param list artist_names: Artist names corresponding to each album specified, in the same order as album_names.
    :return: Pandas DataFrame containing track audio features and useful metadata.
    :rtype: object
    """
    album_names_spotify = format_album_names_for_spotify(album_names)

    track_audio_features = []
    for album_name, artist_name in zip(album_names_spotify, artist_names):
        try:
            album = get_spotify_album(spotify_api_client, album_name, artist_name)
            if album is None:
                continue
            else:
                track_audio_features_album = get_spotify_track_audio_features_for_album(spotify_api_client,
                                                                                        album['uri'])
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
    Gets track popularity score and number of artist followers of the track's artist from a list of track identifiers.

    :param object spotify_api_client: Client used to authenticate and make requests to Spotify's API.
    :param list track_uris: List of Track URIs which are unique identifiers associated with tracks hosted on Spotify.
    :return: Pandas DataFrame containing track popualrity score and artist follower data.
    :rtype: object
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
    Replaces track audio feature data in a Pandas DataFrame with track audio feature data from another album. Used to
    replace incorrect data.

    :param object spotify_api_client: Client used to authenticate and make requests to Spotify's API.
    :param str album_name: Name of the album to search for.
    :param str artist_name: Artist of the album to search for.
    :param str correct_album_uri: Unique identifier correspond to album on Spotify to replace data with.
    :param object df_spotify: Pandas DataFrame containing Spotify data. Specific to data generated in
                              `Data Acquisition & Cleaning.ipynb`.
    :return: Pandas DataFrame updated with new album track audio feature data.
    :rtype: object
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


def generate_spotify_album_features(album_tracks):
    """
    Aggregates track-level audio feature data to album-level metrics.

    :param object album_tracks: Pandas DataFrame containing track-level data.
    :return: Pandas DataFrame with a single row containing album-level metrics.
    :rtype: object
    """
    album_name = album_tracks['Album Title'].iloc[0]
    artist = album_tracks['Artist'].iloc[0]
    num_tracks = len(album_tracks.shape)
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
