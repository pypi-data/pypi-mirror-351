import numpy as np
from scipy.spatial import distance_matrix
from energystats.tests.btree import btree_sum
import pandas as pd
from scipy.special import gamma

def double_center_matrix(m: np.array) -> np.array:
    """
    Given a matrix m, returns the doubly centered matrix k, such that,
    k_ij = m - mean(the ith row of m) - mean(the jth column of m) + total mean.

    """
    row_means = np.mean(m, 1, keepdims=True)
    column_means = np.mean(m, 0, keepdims=True)
    total_mean = np.mean(row_means)
    return m - row_means - column_means + total_mean


def dcov(x: np.array, y : np.array) -> np.float64:
    """
    Returns the distance covariance, which is an always positive number representing the degree of dependency of two random variables. 
    """
    if np.ndim(x) == 1:
        x = np.expand_dims(x, 1)
    if np.ndim(y) == 1:    
        y = np.expand_dims(y, 1)

    a = distance_matrix(x, x)
    b = distance_matrix(y, y)
    a_centered, b_centered = double_center_matrix(a), double_center_matrix(b)
    

    return np.sqrt(np.mean(a_centered * b_centered))

def dcor(x: np.array, y: np.array) -> np.float64:
    """
    Returns an estimation of the distance correlation, R, which has  the following two properties:
    1- 0 <= R <= 1.
    2- R = 0 iff x and y are independent.
    """
    var_x = dcov(x, x)
    var_y = dcov(y, y)

    if np.isclose(var_x * var_y, 0):
        return 0
    
    return dcov(x, y) / np.sqrt(var_x * var_y)


def fast_dcor(x, y):

    if x.ndim > 1 or y.ndim > 1:
        if np.ndim(x) == 1:
            x = np.expand_dims(x, 1)
        if np.ndim(y) == 1:    
            y = np.expand_dims(y, 1)
            
        variance_x = multi_fast_dcov(x, x)
        variance_y = multi_fast_dcov(y, y)
        dcov_x_y = multi_fast_dcov(x, y)

        return dcov_x_y / np.sqrt(variance_x * variance_y)
    
    else:
        variances = fast_dcov(x, y)
        dcor = variances['dcov'] / np.sqrt(variances['dvar_x'] * variances['dvar_y'])
        return dcor

def multi_fast_dcov(x, y):

    if isinstance(x, pd.DataFrame):
        x = x.to_numpy()
    
    if isinstance(y, pd.DataFrame):
        y = y.to_numpy()
    
    p = x.shape[1]
    q = y.shape[1]
    k = 6*p*q

    R = np.random.randn(k, p)
    R /= np.linalg.norm(R, axis=1, keepdims=True)
    Q = np.random.randn(k, q)
    Q /= np.linalg.norm(Q, axis=1, keepdims=True)

    P_x = x @ R.T
    P_y = y @ Q.T

    u = np.zeros(k)

    for i in range(0, k):
        u[i] = fast_dcov(P_x[:, i], P_y[:, i])['dcov']

    C_p = np.sqrt(np.pi) * np.exp(np.log(gamma((p+1) / 2)) - np.log(gamma(p / 2)))
    C_q = np.sqrt(np.pi) * np.exp(np.log(gamma((q+1) / 2)) - np.log(gamma(q / 2)))

    return C_p * C_q * np.mean(u)



def fast_dcov(x, y):
    n = len(x)
    d1 = n**2
    d2 = n**3
    d3 = n**4

    sums = dcov_sums(x, y)

    dcov = np.sqrt(sums['s_1'] / d1 - 2 * sums['s_2'] / d2 + sums['s_3'] / d3)
    dvar_x = np.sqrt(sums['s_1a'] / d1 - 2 * sums['s_2a'] / d2 + sums['s_3a'] / d3)
    dvar_y = np.sqrt(sums['s_1b'] / d1 - 2 * sums['s_2b'] / d2 + sums['s_3b'] / d3)

    return {'dcov': dcov, 'dvar_x': dvar_x, 'dvar_y': dvar_y}

def dcov_sums(x: np.array, y: np.array) -> np.float64:
    
    n = len(x)
    rs_x = rank_sort(x)
    rs_y = rank_sort(y)

    a = row_sums(x, rs_x)
    b = row_sums(y, rs_y)

    a_b_sum = np.sum(a* b)
    a_sum = np.sum(a)
    b_sum = np.sum(b)
    ab_term = a_sum * b_sum

    x_sorted = rs_x['sorted']
    y_x = y[rs_x['sorted_indices']]
    rs_y_x = rank_sort(y_x)
    ones = np.ones(n)

    g_1 = partial_sum(x_sorted, y_x, ones, rs_x, rs_y_x)
    g_x = partial_sum(x_sorted, y_x, x_sorted, rs_x, rs_y_x)
    g_y = partial_sum(x_sorted, y_x, y_x, rs_x, rs_y_x)
    g_xy = partial_sum(x_sorted, y_x, x_sorted * y_x, rs_x, rs_y_x)
    s = np.sum(x * y * g_1 + g_xy - x * g_y - y * g_x)

    l = {
        's_1': s,
        's_2': a_b_sum,
        's_3': ab_term,
        's_1a': 2 * n * (n-1) * np.var(x, ddof=1),
        's_1b': 2 * n * (n-1) * np.var(y, ddof=1),
        's_2a': np.sum(a**2),
        's_2b': np.sum(b**2),
        's_3a': a_sum**2,
        's_3b': b_sum**2,
        'row_sums_a': a,
        'row_sums_b': b,
        'sum_a': a_sum,
        'sum_b': b_sum

    }
    
    return l

def partial_sum(x: np.array, y: np.array, z: np.array, sr_x, sr_y):
    rank_x = sr_x['ranks']
    order_y = sr_y['sorted_indices']
    rank_y = sr_y['ranks']

    cum_sum_y = (np.cumsum(z[order_y]) - z[order_y])[rank_y]
    cum_sum_x = np.cumsum(z) - z


    gamma = btree_sum(rank_y + 1, z)
    g = sum(z) - z - 2 * cum_sum_y - 2 * cum_sum_x + 4 * gamma

    return g[rank_x]

def row_sums(x, rs_x):

    x_sorted = rs_x['sorted']
    ranks = rs_x['ranks']
    n = len(x)


    x_sum = np.sum(x)
    cum_sum = (np.cumsum(x_sorted) - x_sorted)[ranks]

    row_sum = x_sum + (2 * ranks - n) * x - 2 * cum_sum

    return row_sum

def rank_sort(x):
    sorted_indices = np.argsort(x)
    x_sorted = x[sorted_indices]

    r = np.empty_like(sorted_indices)
    r[sorted_indices] = np.arange(len(x))

    return {'sorted': x_sorted, 'sorted_indices': sorted_indices, 'ranks': r}

