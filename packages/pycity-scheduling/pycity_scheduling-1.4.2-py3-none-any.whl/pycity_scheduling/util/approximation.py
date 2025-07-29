"""
The pycity_scheduling framework


Copyright (C) 2025,
Institute for Automation of Complex Power Systems (ACS),
E.ON Energy Research Center (E.ON ERC),
RWTH Aachen University

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""


import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans


def piecewise_linear_approx(f, inf_bound, sup_bound, nb_samples=1000, nb_segments=10):
    """
    Perform piece-wise linear approximation for convex or concave 1D functions.

    Find a partition of the bound interval using KMeans-clustering with x_sample and function slope as features, for a
    given number of clusters. Then perform a linear regression on each segment of the partition.
    The approximation is given by the maximum (resp. minimum) of all linear functions if the function to approximate is
    convex (resp. concave). The convexity of the function is given through the argument "convexity" that takes the value
    "convex" if the function is convex and anything else if the function is concave.
    
    Parameters
    ----------
    f : callable
        Function to be approximated.
    inf_bound : list of float
        List of lower bounds for the variables in var.
    sup_bound : list of float
        List of upper bounds for the variables in var.
    nb_samples : int, default 100
        Number of sampling points.
    nb_segments : int, default 10
        Number of segments used in the partitioning of the bound interval.

    Returns
    -------
    slopes : List[float]
    intercepts : List[float]
    """
    # Sampling:
    x_sample = np.linspace(inf_bound, sup_bound, nb_samples)
    y_sample = f(x_sample)

    # Calculating gradient:
    gradient_list = []
    for i in range(1, len(x_sample) - 1):
        delta_x = x_sample[i + 1] - x_sample[i - 1]
        delta_y = y_sample[i + 1] - y_sample[i - 1]
        gradient = delta_y / delta_x
        gradient_list.append(gradient)
    gradient_list.insert(0, (y_sample[1] - y_sample[0]) / (x_sample[1] - x_sample[0]))
    gradient_list.append((y_sample[-1] - y_sample[-2]) / (x_sample[-1] - x_sample[-2]))

    # Building features such as position and gradient:
    x_sample = x_sample.reshape(-1, 1)
    gradient_list = np.array(gradient_list).reshape(-1, 1)
    features = np.column_stack((x_sample, gradient_list))
    mean = np.mean(features, axis=0)
    std_dev = np.std(features, axis=0)
    normalized_features = (features - mean) / std_dev

    # Perform KMeans clustering:
    kmeans = KMeans(n_clusters=nb_segments, n_init=10, random_state=0)
    clusters = kmeans.fit_predict(normalized_features)

    # Linear interpolation on each cluster:
    slope_list = []
    intercept_list = []
    for i in range(nb_segments):
        mask = (clusters == i)
        x_segment = x_sample[mask]
        y_segment = y_sample[mask]
        model = LinearRegression()
        model.fit(x_segment, y_segment)
        slope = model.coef_[0]
        intercept = model.intercept_
        slope_list.append(slope)
        intercept_list.append(intercept)

    return slope_list, intercept_list
