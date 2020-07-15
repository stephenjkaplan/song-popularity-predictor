"""
Contains utility functions necessary to analyze and build a model.
Author: Stephen Kaplan (July 13, 2020)
"""
import seaborn as sns
import matplotlib.pyplot as plt


ALL_GENRES = ['Electronic', 'Experimental', 'Folk/Country', 'Global', 'Jazz', 'Metal', 'Pop/R&B', 'Rap/Hip-Hop', 'Rock']


def pair_plot_for_music_genre(data, genre):
    """

    :param data:
    :param genre:
    :return:
    """
    df = data[data[genre] == 1]
    df.drop(ALL_GENRES, axis=1, inplace=True)
    sns.pairplot(df, kind='scatter', plot_kws={'alpha': 0.1})
    plt.title(genre)
