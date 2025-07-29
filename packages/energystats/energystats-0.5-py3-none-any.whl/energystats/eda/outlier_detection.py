import numpy as np
import pandas as pd
from scipy import stats
from energystats.tests.cor import dcor


def find_outliers(data, target, threshold = 3, row_names = None,):
    numeric_data = data.to_numpy()
    n = len(numeric_data)
    dcor_replicates = []
    original_dcor = dcor(data, target)

    for i in range(0, n):
        sample_data = data.drop([i], axis=0)
        sample_target = target.drop([i], axis=0)
        dcor_replicates.append(dcor(sample_data, sample_target))
    
    dcor_replicates = pd.DataFrame({'replicates' : dcor_replicates, 'point_labels': row_names})
    z = np.abs(stats.zscore(dcor_replicates['replicates']))
    outliers = dcor_replicates[z > threshold]

    
    return {'original_dcor': original_dcor, 'dcor_replicates': dcor_replicates, 'outliers' : outliers }


