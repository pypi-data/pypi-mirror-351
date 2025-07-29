from numba import njit
import numpy as np
import math


@njit
def powers2(L):
    pwr2 = np.zeros(L, dtype=np.int64)
    pwr2[0] = 2
    for k in range(1, L):
        pwr2[k] = pwr2[k-1] * 2
    return pwr2

@njit
def p2sum(pwr2):
    L = len(pwr2)
    psum = np.zeros(L, dtype=np.int64)
    psum.fill(pwr2[L-1])
    for i in range(1, L):
        psum[i] = psum[i-1] + pwr2[L-i-1]
    return psum

@njit
def container_nodes(y, pwr2, psum):
    L = len(pwr2)
    nodes = np.zeros(L, dtype=np.int64)
    
    nodes[0] = y
    for i in range(L-1):
        nodes[i+1] = math.ceil(y / pwr2[i]) + psum[i]
    
    return nodes

@njit
def sub_nodes(y, pwr2, psum):
    L = len(psum)
    nodes = np.full(L, -1, dtype=np.int64)
    
    k = y
    for level in range(L-1, 0, -1):
        p2 = pwr2[level-1]
        if k >= p2:
            idx = psum[level-1] + (y // p2)
            nodes[L-level-1] = idx
            k -= p2
    
    if k > 0:
        nodes[L-1] = y
    
    return nodes


@njit
def btree_sum(y, z):
    n = len(y)
    L = math.ceil(math.log2(n))
    
    pwr2 = powers2(L)
    psum = p2sum(pwr2)
    
    sums = np.zeros(2 * pwr2[L-1], dtype=np.float64)
    gamma1 = np.zeros(n, dtype=np.float64)
    
    for i in range(1, n):
        nodes = container_nodes(y[i-1], pwr2, psum)
        for p in range(L):
            sums[nodes[p]] += z[i-1]
        
        nodes = sub_nodes(y[i]-1, pwr2, psum)  
        for p in range(L):
            node = nodes[p]
            if node > 0:
                gamma1[i] += sums[node]
    
    return gamma1