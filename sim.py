#!/usr/bin/env python

import argparse
from scipy import spatial
import os
import numpy as np
from sklearn.cluster import OPTICS

parser = argparse.ArgumentParser(description='vector file.')
parser.add_argument('-vector_file', type=str, help='vector_file file', default="alllog/templates.txt.vec")
args = parser.parse_args()
vector_file = args.vector_file
basedir = os.path.dirname(vector_file)

vecs = []
with open(vector_file) as f:
    for line in f:
        vec = tuple(map(float, line.strip().split()))
        vecs.append(vec)

# X = np.vstack((vecs[:1000]))
# clust = OPTICS(min_samples=2, xi=.05, min_cluster_size=2, metric='cosine')
# clust.fit(X)
# print(clust.labels_)

# with open(vector_file+".cluster", 'w') as f:
#     f.write("\n".join(map(str, clust.labels_)))

v1 = vecs[0]
with open(vector_file+".sim", "w") as f:
    for i in range(len(vecs)):
        sim = []
        for j in range(len(vecs)):
            cos = spatial.distance.cosine(vecs[i], vecs[j])
            cosine_similarity = 1 - cos
            sim.append(cosine_similarity)

        idx=np.argsort(sim)[-11:-1]
        num=np.sort(sim)[-11:-1]

        # for similarity >= 0.99, we treat them as the same template
        # for all temps which have sim >= 0.99, we use the smallest idx as the idx of the group
        small = i
        for j in range(10):
            if num[j] > 0.985:
                small = np.min(idx[j:])
        if small > i:
            small = i

        s=["{:.2f}".format(x) for x in num]
        #f.write("{}; {}; {}, {}\n".format(i, small, idx, s))
        f.write("{}; {}; {}, {}\n".format(i+1, small+1, [x+1 for x in idx], s))
