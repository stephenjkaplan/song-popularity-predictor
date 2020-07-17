import streamlit as st
from math import log
from joblib import load
import numpy as np

# MAIN PAGE

# heading
st.title('Predicting Spotify Popularity: Rap Music')

st.text('')

# display of popularity meter and number
popularity_display = st.empty()
status_text = st.text('Spotify Popularity (Out of 100)')
popularity_number = st.empty()

st.text('')

st.markdown('#### Use the options below to predict the popularity of a rap song on Spotify.')

st.text('')

# widgets for user to select values for features
followers = st.slider('# of Spotify Followers (max. 1 million)', min_value=1000, max_value=1000000,
                      value=500000, step=1000)
log_followers = log(followers)

danceability = st.slider('Danceability', min_value=0.0, max_value=1.0, value=0.5, step=0.01)
energy = st.slider('Energy', min_value=0.0, max_value=1.0, value=0.5, step=0.01)
speechiness = st.slider('Speechiness', min_value=0.0, max_value=1.0, value=0.5, step=0.01)
valence = st.slider('Valence', min_value=0.0, max_value=1.0, value=0.5, step=0.01)

st.write('<style>div.Widget.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
mode_label = st.radio('Mode', ('Major Key', 'Minor Key'))
mode = 1 if mode_label == 'Major Key' else 0

# predict popularity
model = load('data/final_model.pkl')
features = np.array([mode, danceability, energy, speechiness, valence, log_followers])
popularity = model.predict(features.reshape(1, -1))
popularity_display.progress(int(popularity[0]))
popularity_number.subheader(f'{int(popularity[0])}')

st.text('')
st.text('Created by Stephen Kaplan')
st.markdown('https://github.com/stephenjkaplan/song-popularity-predictor')

# SIDE BAR
st.sidebar.title('Info & Glossary')

st.sidebar.markdown(
    'This tool predicts Spotify popularity on a scale of 0 to 100. As defined in the '
    '[Spotify API Reference](https://developer.spotify.com/documentation/web-api/reference/tracks/get-track/), the '
    'popularity of a track is algorithmically calculated, and is a combination of how many plays a track has and how '
    'recent those plays are. This project was made by Stephen Kaplan over a 2-week span in July 2020 as a project for '
    'the [Metis](https://www.thisismetis.com/) data science program.'
)


st.sidebar.subheader('Technical Details')
st.sidebar.markdown(
    'The model was trained on Spotify audio features and other data defined below, using a Lasso linear model. The '
    'R2 score is `0.58` and it has a RMSE is `13.82`. The code is located '
    '[here](https://github.com/stephenjkaplan/song-popularity-predictor) and the blog post about it is '
    '[here](https://stephenjkaplan.github.io/).'
)

st.sidebar.subheader('Feature Glossary')
st.sidebar.markdown(
    '_Most of the definitions below can be attributed to the '
    '[Spotify API Docs](https://developer.spotify.com/documentation/web-api/reference/tracks/get-audio-features/)._'
)
st.sidebar.markdown("**# of Spotify Followers** is the number of Spotify users following a track's artist. This tool "
                    "only allows for up to 1 million followers, but artists such as Beyonce have 20+ million "
                    "followers.")
st.sidebar.markdown('**Danceability** describes how suitable a track is for dancing based on a combination of musical '
                    'elements including tempo, rhythm stability, beat strength, and overall regularity.')
st.sidebar.markdown('**Energy** represents a perceptual measure of intensity and activity.')
st.sidebar.markdown('**Speechiness** represents the presence of spoken words in a track.')
st.sidebar.markdown('**Valence** describes the musical positiveness/happiness/cheerfulness conveyed by a '
                    'track.')
st.sidebar.markdown('**Mode** determines if the song is in a major or minor key.')