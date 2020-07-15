"""
Contains utility functions necessary to analyze and build a model.
Author: Stephen Kaplan (July 13, 2020)
"""
import seaborn as sns
import matplotlib.pyplot as plt
from math import sqrt
from sklearn.model_selection import KFold


ALL_GENRES = ['Electronic', 'Experimental', 'Folk/Country', 'Global', 'Jazz', 'Metal', 'Pop/R&B', 'Rap/Hip-Hop', 'Rock']


def pair_plot_for_music_genre(data, genre):
    """

    :param data:
    :param genre:
    :param kind:
    :return:
    """
    df = data[data[genre] == 1]
    df.drop(ALL_GENRES, axis=1, inplace=True)
    sns.pairplot(df, kind='scatter', plot_kws={'alpha': 0.1})
    plt.title(genre)


def manual_cross_validate(X, y, estimator, cv=5):
    """

    :param X:
    :param y:
    :param estimator:
    :param cv:
    :return:
    """
    kf = KFold(n_splits=cv, shuffle=True)
    r2_train, r2_val, rmse = [], [], []
    for train_ind, val_ind in kf.split(X, y):
        X_train, y_train = X.iloc[train_ind], y.iloc[train_ind]
        X_val, y_val = X.iloc[val_ind], y.iloc[val_ind]

        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_val_scaled = scaler.transform(X_val)

        estimator.fit(X_train_scaled, y_train)
        r2_train.append(estimator.score(X_train_scaled, y_train))
        r2_val.append(estimator.score(X_val_scaled, y_val))
        rmse.append(sqrt(mean_squared_error(y_val, estimator.predict(X_val_scaled))))

    print(f'R2 Train Avg: {np.mean(r2_train)}')
    print(f'R2 Val Avg: {np.mean(r2_val)}')
    print(f'RMSE Avg: {np.mean(rmse)}')
    print('----Coefficients----')
    for coef, col in zip(estimator.coef_, X.columns):
        print(f'{col}: {coef}')


def manual_cross_validate_poly(X, y, estimator, cv=5):
    """

    :param X:
    :param y:
    :param estimator:
    :param cv:
    :return:
    """
    kf = KFold(n_splits=cv, shuffle=True)
    r2_train, r2_val, rmse = [], [], []
    for train_ind, val_ind in kf.split(X, y):
        X_train, y_train = X[train_ind], y.iloc[train_ind]
        X_val, y_val = X[val_ind], y.iloc[val_ind]

        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_val_scaled = scaler.transform(X_val)

        estimator.fit(X_train_scaled, y_train)
        r2_train.append(estimator.score(X_train_scaled, y_train))
        r2_val.append(estimator.score(X_val_scaled, y_val))
        rmse.append(sqrt(mean_squared_error(y_val, estimator.predict(X_val_scaled))))

    print(f'R2 Train Avg: {np.mean(r2_train)}')
    print(f'R2 Val Avg: {np.mean(r2_val)}')
    print(f'RMSE Avg: {np.mean(rmse)}')