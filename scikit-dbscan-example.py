# -*- coding: utf-8 -*-
"""
This script is used to validate that my implementation of DBSCAN produces
the same results as the implementation found in scikit-learn.

It's based on the scikit-learn example code, here:
http://scikit-learn.org/stable/auto_examples/cluster/plot_dbscan.html    

@author: Chris McCormick
"""

from time import time
from sklearn.datasets.samples_generator import make_blobs
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler

from dbscan import MyDBSCAN

# Create three gaussian blobs to use as our clustering data.
centers = [[1, 1], [-1, -1], [1, -1]]
X, labels_true = make_blobs(n_samples=750, centers=centers, cluster_std=0.4,
                            random_state=0)

X = StandardScaler().fit_transform(X)
print X
###############################################################################
start = time()
print 'Runing scikit-learn implementation...'
db = DBSCAN(eps=0.3, min_samples=10).fit(X)
skl_labels = db.labels_
end = time()
print end - start
print skl_labels
