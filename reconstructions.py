#!/usr/bin/env python3

############################
#### reconstructions.py ####
############################

import numpy as np
import tools
from sklearn.cluster import KMeans

def kmeans(data, k=2):
    '''
    Cluster the data using k-means clustering

    Arguments:
    1. data:        1D array data. Expected to be one of the following data
                    i.      off-diagonal elements of cov_inv_m
                    ii.     off-diagonal elements of cov_m_inv
                    (see inverse_covariance() in dynamics_tools.py)

    2. k:           Number of clusters (default: 2)

    
    Returns:
    1. A_reco:      Reconstructed adjacency matrix
    '''
    assert type(data) == np.ndarray, "Input data must be of type 'numpy.ndarray'"
    assert data.size > 0, "Input data must not be empty"
    assert data.dtype == int or data.dtype == float, "Input data must be of dtype 'int' or 'float'"
    assert np.isfinite(data).all() == True, "Input data elements must be real numbers"
    size = data.shape
    assert len(size) == 1, "Input data must be 1D shape"
    assert size[0] > 1, "Input data must have at least two elements for clustering"
    assert type(k) == int and k > 1, "Number of cluster must be positive integer and not less than 2"

    
    # Convert data to a shape for clustering
    data = data.reshape(-1, 1)

    # Create k-means clustering object
    kmeans = KMeans(n_clusters=k, random_state=29)
    
    # Perform k-means clustering on the data
    kmeans.fit(data)

    # Get the reconstructed indices (should 0's and 1's for n_clusters = 2)
    reco_indices = kmeans.labels_

    # Get the centroids of the clusters
    centroids = kmeans.cluster_centers_

    # Data with centroid absolute value close to zero are regarded as
    # unconnected pairs
    ucon_id = np.argmin(abs(centroids))

    # Recover the number of nodes from number of data points
    # NOTE: we assume n_data = n_node * (n_node - 1) / 2
    #       If that is the case, solving qudratic equation
    #       gives the following expression for n_node and
    #       it must be an integer.
    #
    #       However, this assumption might break depending
    #       on the user input and we have not guard this case
    n_data = data.shape[0]
    n_node = int(0.5*(1 + np.sqrt(1 + 8*n_data)))
    row, col = tools.index_recover(n_node)

    # Get the connected pair indices
    row_conn_triu = row[reco_indices != ucon_id].astype("int")
    col_conn_triu = col[reco_indices != ucon_id].astype("int")


    # Initialize the reconstructed adjacency matrix with zero elements
    A_reco = np.zeros((n_node, n_node))

    # Assign links according to row_conn, and col_conn
    # NOTE: only upper triangle elements are assigned
    #       (see off_diag_upper() in tools.py)
    A_reco[row_conn_triu, col_conn_triu] = 1

    # Symmetrize the reconstructed adjacency matrix
    A_reco = A_reco + A_reco.T

    A_reco = A_reco.astype('int')

    return A_reco

################################################
#  You can add other clustering methods below  #
#  by following the kmeans example             #
################################################
