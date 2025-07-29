import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from energystats.tests.cor import fast_dcov
from scipy.optimize import minimize

def constraint(u):
    return 1 - np.linalg.norm(u)

def objective(u, x, y):
    u /= np.linalg.norm(u)
    return -fast_dcov(x @ u, y)['dcov']

def dca(x, y, k=2):
    m = x.shape[1]
    U = np.random.randn(m, k)
    U /= np.linalg.norm(U, axis=0)
    X_c = x

    for i in range(k):
        u_k = U[:, i]

        cons = {'type': 'ineq', 'fun': constraint}
        res = minimize(objective, x0=u_k, args=(X_c, y), constraints=cons)

        u = res.x / np.linalg.norm(res.x)
        U[:, i] = u
        U_k = U[:, :i+1]
        p = U_k @ U_k.T
        X_c = x - x @ p
        
    return {'projections': x @ U, 'axes': U,}















