from multiprocessing import Pool

import numpy as np
from xgboost import XGBClassifier
import xgboost as xgb
from tqdm import tqdm
from transcendent.classifiers.ncm_classifier import NCMClassifier
import transcendent.data as data
from transcendent.utils import (
    alloc_shm,
    load_existing_shm,
)
import os
import logging

eps = np.finfo(np.float64).eps


class XGBNCMClassifier(NCMClassifier):
    def __init__(self, **kwargs):
        NCMClassifier.__init__(self)
        self.__model = XGBClassifier(**kwargs)

    def fit(self, X_train, y_train):
        save_path = os.path.join(
            "models", "ember", "time_split", "ice-malw-static-features", "xgboost.pkl"
        )
        if os.path.exists(save_path):
            self.__model = data.load_cached_data(save_path)
        else:
            self.__model.fit(X_train, y_train)
            data.cache_data(self.__model, save_path)

    def predict(self, X):
        return self.__model.predict(X)

    def ncm(self, X, y, k=5):
        #     # Predict all probabilities at once (shape: [n_samples, n_classes])
        #     probas = self.__model.predict_proba(X)

        #     # Vectorized extraction of correct class probabilities
        #     # (1 - probability of the true class for each calibration example)
        #     return 1 - probas[np.arange(len(y)), y]
        probs = self.__model.predict_proba(X)
        scores_margin = []
        for i, true_label in enumerate(y):
            other_probs = np.delete(
                probs[i], true_label
            )  # Remove true class probability
            max_other = np.max(other_probs)
            margin_score = max_other - probs[i, true_label]
            scores_margin.append(margin_score)
        return scores_margin
