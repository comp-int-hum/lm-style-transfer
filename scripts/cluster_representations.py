import argparse
import json
import re
from sklearn.cluster import KMeans
from sklearn import metrics
import numpy

parser = argparse.ArgumentParser()
parser.add_argument("--representations", dest="representations")
parser.add_argument("--cluster_count", dest="cluster_count", type=int)
parser.add_argument("--random_seed", dest="random_seed", type=int)
parser.add_argument("--clustering", dest="clustering")
args = parser.parse_args()


with open(args.representations, "rt") as ifd:
    representations = json.loads(ifd.read())

features = set()
for item in representations:
    for k in item["representation"].keys():
        features.add(k)
feature_to_index = {k : i for i, k in enumerate(features)}
index_to_feature = {i : k for k, i in feature_to_index.items()}

        
data = numpy.zeros(shape=(len(representations), len(features)))
for row, item in enumerate(representations):
    for feature, value in item["representation"].items():
        data[row, feature_to_index[feature]] = value

model = KMeans(n_clusters=args.cluster_count, random_state=args.random_seed)
model.fit(data)

clustering = {
    "file" : args.representations,
    "ami" : metrics.adjusted_mutual_info_score([item["title"] for item in representations], model.labels_),
    "clusters" : []
}

for cluster_num in range(args.cluster_count):
    cluster = []
    for c, item in zip(model.labels_, representations):
        if c == cluster_num:
            cluster.append(
                {
                    "author" : item["author"],
                    "title" : item["title"]
                }
            )
    clustering["clusters"].append(cluster)

with open(args.clustering, "wt") as ofd:
    ofd.write(json.dumps(clustering, indent=4))
