#!/usr/bin/env python3

import numpy as np
import os
import sys

ROOT_DIR = os.path.abspath("../")
sys.path.append(ROOT_DIR)
from utils import base


def laplacian(W):
    '''
    Construct the (weighted) Laplacian matrix from the (weighted) adjacnecy matrix

    Arguments:
    1. W:    weighted adjacency matrix

    Returns:
    1. L:    weighted Laplacian matrix
    '''
    assert type(W) == np.ndarray, "W must be of type 'numpy.ndarray'"
    assert W.size > 0, "W must not be empty"
    assert W.dtype == int or W.dtype == float, "W must be of dtype 'int' or 'float'"
    assert np.isfinite(W).all(), "Elements of W must be finite real numbers"
    size = W.shape
    assert len(size) == 2, "W must be 2D shape"
    assert size[0] == size[1], "W must be a square matrix"
    assert (np.diag(W) == 0).all(), "W must not have self-loop"

    # Construct the (weighted) Laplacian matrix
    # NOTE: Be-careful when W is a directed network
    #       in-link and out-link can be different
    L = np.diag(np.sum(W, 1)) - W

    return L


def hidden_effect(W, measure_id, hidden_id, a=0):
    '''
    Compute hidden node effect (C matrix)

    Arguments:
    1. W:               Weighted adjacency matrix
    2. measure_id:      Measured node indices
    3. hidden_id:       Hidden node indices
    4. a:               Dynamical constant -f'(X0)  (default: 0)

    Returns:
    1. C:       C matrix
    '''
    assert type(W) == np.ndarray, "W must be of type 'numpy.ndarray'"
    assert W.size > 0, "W must not be empty"
    assert W.dtype == int or W.dtype == float, "W must be of dtype 'int' or 'float'"
    assert np.isfinite(W).all(), "Elements of W must be finite real numbers"
    size = W.shape
    assert len(size) == 2, "W must be 2D shape"
    assert size[0] == size[1], "W must be a square matrix"
    assert (np.diag(W) == 0).all(), "W must not have self-loop"
    assert np.allclose(W, W.T), "W must be symmetric\n C matrix currently is defined for bi-directional network only"

    assert type(measure_id) == np.ndarray, "measure_id must be of type 'np.ndarray'"
    assert measure_id.size > 0, "measure_id must not be empty"
    assert measure_id.dtype == int, "measure_id must be of dtype 'int'"
    assert len(measure_id.shape) == 1, "measure_id must be 1D shape"
    assert (measure_id >= 0).all(), "measure_id elements must be non-negative integers"
    assert np.max(measure_id) < size[0], "measure_id elements must be smaller than the input matrix size"

    assert type(hidden_id) == np.ndarray, "hidden_id must be of type 'np.ndarray'"
    assert hidden_id.size > 0, "hidden_id must not be empty"
    assert hidden_id.dtype == int, "hidden_id must be of dtype 'int'"
    assert (hidden_id >= 0).all(), "hidden_id elements must be non-negative integers"
    assert len(hidden_id.shape) == 1, "hidden_id must be 1D shape"
    assert np.max(hidden_id) < size[0], "hidden_id elements must be smaller than the input matrix size"

    num_m = len(measure_id)
    num_h = len(hidden_id)
    assert size[0] == (num_m + num_h), "Total number of elements in measure_id and hidden_id does not equal the number of rows of M"

    all_id = np.unique(np.concatenate((measure_id, hidden_id)))
    assert len(all_id) == size[0], "mesure_id and hidden_id contain common elements"

    assert (type(a) == int or type(a) == float) and np.isfinite(a), "Dynamical constant a must be a real number"

    # Compute the Laplacian matrix
    L = laplacian(W)

    # Re-arrange the Laplacian matrix
    E = base.block_off_up(L, measure_id, hidden_id)
    Lh = base.block_diag_low(L, hidden_id)

    # Compute the C matrix
    H = Lh + a * np.identity(num_h)
    H_inv = base.inverse(H)
    C = np.matmul(np.matmul(E, H_inv), E.T)

    if not np.allclose(C, C.T):
        print("[WARN] The computed C matrix is not symmetric")

    return C
