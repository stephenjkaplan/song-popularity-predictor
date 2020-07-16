"""
Contains utility functions necessary to analyze and build a model.
Author: Stephen Kaplan (July 13, 2020)
"""
import seaborn as sns
import matplotlib.pyplot as plt
from math import sqrt
import numpy as np

from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split, cross_val_score, KFold


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


def score_baseline_linear_regression_model(X, y):
    """
    For a set of features and target X, y, perform a 80/20 train/val split,
    fit and validate a linear regression model, and report results

    The function below calculates a validation and training score by doing a cross validation on the validation data and training data, respectively. It does this because I was noticing far too much variation in the scores done on a single fit (as a result of the pseudo-randomness of train-test-split).
    """
    # perform train/val split
    X_train, X_val, y_train, y_val = \
        train_test_split(X, y, test_size=0.25)

    # fit linear regression to training data
    lr_model = LinearRegression()
    lr_model.fit(X_train, y_train)

    # score model on training and validation score. do cross validation to get a better estimate
    train_score = np.mean(cross_val_score(lr_model, X_train, y_train))
    val_score = np.mean(cross_val_score(lr_model, X_val, y_val))
    rmse = sqrt(mean_squared_error(y_true=y_val, y_pred=lr_model.predict(X_val)))

    # report results
    print('\nTrain R2 score was', train_score)
    print('\nValidation R^2 score was:', val_score)
    print('\nRMSE:', rmse)
    print('\nFeature coefficient results: \n')
    for feature, coef in zip(X.columns, lr_model.coef_):
        print(feature, ':', f'{coef:.2f}')


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