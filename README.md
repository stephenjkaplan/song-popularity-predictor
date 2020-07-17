# Song Popularity Predictor

Play around with the model and make predictions using the [web app](https://song-popularity-predictor.appspot.com/)
I made using [Streamlit](https://www.streamlit.io/).

#### Description
Predicting Spotify song "popularity" scores using linear regression and track audio features/metadata from the Spotify 
API. 

The popularity of a track is algorithmically calculated, and is a combination of how many plays a track has and 
how recent those plays are. This was developed over a 2-week span in July 2020 as a project for 
the [Metis](https://thisismetis.com) data science program.

The model in `data/final_model.pkl` was trained on Spotify audio features and other data defined below, using a Lasso 
linear model. The R2 score is `0.58` and it has a RMSE is `13.82`. The blog post about it is 
[here](https://stephenjkaplan.github.io/).

#### Data Sources
* [Pitchfork](https://pitchfork.com/) Album Reviews
* [Spotify API](https://developer.spotify.com/documentation/web-api/)

#### File Contents
* `data/`
    - `final_model.pkl` is a pickled version of a pre-trained scikit-learn Lasso regression model.
* `notebooks/`
    - `Data Acquisition & Cleaning.ipynb` contains all web-scraping, API requests, and 
       data cleaning/preparation for this project.
    - `EDA & Modeling Workbook (Project V1).ipynb` contains analysis and modeling for the project's initial 
       scope, which was to predict Pitchfork Album Ratings. I late pivoted to the scope of Project V2 (below).
    - `FINAL EDA & Modeling Workbook (Project V2).ipynb` contains the final analysis and modeling for predicting 
       Spotify popularity scores. 
* `utilities/`
    - `data_acquisition_utilities.py` contains functions used in `Data Acquisition & Cleaning.ipynb`.
    - `modeling_utilities.py` contains functions used in the modeling Jupyter Notebooks.
* `app.py` contains code for a [Streamlit](https://www.streamlit.io/) app that can be used to play around 
  with the model and make predictions.

#### Dependencies

The Python packages required for this project are listed in both `requirements.txt` & `environment.yml`. 
You can install the packages via:

`pip install -r requirements.txt`

or by creating an Anaconda environment:

`conda env create -f environment.yml`.

Additionally, in order to completely run `Data Acquisition & Cleaning.ipynb` notebook, you'll need to:

1. Install [ChromeDriver](https://chromedriver.chromium.org/getting-started).
2. Generate [Spotify API Credentials](https://developer.spotify.com/documentation/general/guides/authorization-guide/).
