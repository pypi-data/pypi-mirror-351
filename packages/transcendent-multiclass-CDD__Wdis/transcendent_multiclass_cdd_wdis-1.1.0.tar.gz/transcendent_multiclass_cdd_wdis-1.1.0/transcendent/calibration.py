# -*- coding: utf-8 -*-

"""
calibration.py
~~~~~~~~~~~~~~

Functions for partitioning and training proper training and calibration sets.

"""

import logging
import multiprocessing as mp
import os
from itertools import repeat

import numpy as np
from sklearn.model_selection import LeaveOneOut, StratifiedKFold
from tqdm import tqdm

import transcendent.data as data
import transcendent.scores as scores


def train_calibration_ice(
    model, X_proper_train, X_cal, y_proper_train, y_cal, saved_data_folder="."
):
    """Train calibration set (for a single fold).

    Quite a bit of information is needed here for the later p-value
    computation and probability comparison. The returned dictionary has
    the following structure:

        'cred_p_val_cal_fold'  -->  # Calibration credibility p values
        'conf_p_val_cal_fold'  -->  # Calibration confidence p values
        'ncms_cal_fold'        -->  # Calibration NCMs
        'pred_cal_fold'        -->  # Calibration predictions
        'groundtruth_cal_fold' -->  # Calibration groundtruth
        'probas_cal_fold'      -->  # Calibration probabilities
        'pred_proba_cal_fold'  -->  # Calibration predictions

    Args:
        X_proper_train (np.ndarray): Features for the 'proper training
            set' partition.
        X_cal (np.ndarray): Features for a single calibration set
            partition.
        y_proper_train (np.ndarray): Ground truths for the 'proper
            training set' partition.
        y_cal (np.ndarray): Ground truths for a single calibration set
            partition.
        fold_index: An index to identify the current fold (used for caching).

    Returns:
        dict: Fold results, structure as in the docstring above.

    """
    # Train model with proper training

    # model_name = 'svm_cal_fold_{}.p'.format(fold_index)
    # model_name = os.path.join(saved_data_folder, model_name)
    #
    # if os.path.exists(model_name):
    #     svm = data.load_cached_data(model_name)
    # else:
    #     svm = SVC(probability=True, kernel='linear', verbose=True)
    #     svm.fit(X_proper_train, y_proper_train)
    #     data.cache_data(svm, model_name)

    # Replacing the above code with Random Forest model
    model_name = "model_cal.pkl"
    model_name = os.path.join(saved_data_folder, model_name)

    model.fit(X_proper_train, y_proper_train)
    data.cache_data(model, model_name)

    # Get ncms for calibration fold
    logging.debug("Getting calibration ncms")
    pred_cal_fold = model.predict(X_cal)

    # Compute p values for calibration fold
    logging.debug("Computing calibration p-values")

    saved_ncms_name = "ncms_cal.pkl"
    saved_ncms_name = os.path.join(saved_data_folder, saved_ncms_name)

    # if os.path.exists(saved_ncms_name):
    #     ncms_cal_fold = data.load_cached_data(saved_ncms_name)
    # else:
    ncms_cal_fold = model.ncm(X_cal, y_cal)
    data.cache_data(ncms_cal_fold, saved_ncms_name)

    saved_pvals_name = "p_vals_cal.pkl"
    saved_pvals_name = os.path.join(saved_data_folder, saved_pvals_name)

    # if os.path.exists(saved_pvals_name):
    #     p_val_cal_fold_dict = data.load_cached_data(saved_pvals_name)
    # else:

    p_val_cal_fold_dict = scores.compute_p_values_cred_and_conf(
        clf=model,
        train_ncms=ncms_cal_fold,
        y_train=y_cal,
        test_ncms=ncms_cal_fold,
        y_test=y_cal,
        X_test=X_cal,
    )
    data.cache_data(p_val_cal_fold_dict, saved_pvals_name)

    # Compute values for calibration probabilities
    # logging.debug("Computing cal probas for fold {}...".format(fold_index))
    # probas_cal_fold, pred_proba_cal_fold = scores.get_rf_probs(
    #     rf, X_cal
    # )  # scores.get_svm_probs(svm, X_cal)

    return {
        # Calibration credibility p values
        "cred_p_val_cal": p_val_cal_fold_dict["cred"],
        # Calibration confidence p values
        "conf_p_val_cal": p_val_cal_fold_dict["conf"],
        "ncms_cal": ncms_cal_fold,  # Calibration NCMs
        "pred_cal": pred_cal_fold,  # Calibration predictions
        "groundtruth_cal": y_cal,  # Calibration groundtruth
        # "probas_cal": probas_cal_fold,  # Calibration probabilities
        # "pred_proba_cal": pred_proba_cal_fold,  # Calibration predictions
        # "best_knn": best_k,
        "model": model,  # The trained model
    }
