import argparse
import json
import re
import pandas
import seaborn
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument("--summary", dest="summary")
args, rest = parser.parse_known_args()

seaborn.set_theme(style="whitegrid")

results = []
for i in range(int(len(rest) / 2)):
    with open(rest[i * 2 + 1], "rt") as ifd:
        configuration = json.loads(ifd.read())
    with open(rest[i * 2], "rt") as ifd:
        clustering = json.loads(ifd.read())
        configuration["ami"] = clustering["ami"]
    results.append(configuration)

df = pandas.DataFrame(results)    
fields = [
    f for f in [
        "CLUSTER_COUNT",
        "WORDS_PER_SUBDOCUMENT",
        "NUM_FEATURES_TO_KEEP",
        "LOWERCASE",
        "FEATURE_SELECTION_METHOD"
    ] if df[f].nunique() > 1
]

fig, axs = plt.subplots(len(fields), 1, figsize=(15, 5 * len(fields)))

for i, field in enumerate(fields):
    uvs = df[field].unique()
    if all([v.isdigit() for v in uvs]):
        lookup = {float(v) : v for v in uvs}
        order = [lookup[k] for k in sorted(lookup.keys())]
    else:
        order = uvs
    sp = seaborn.pointplot(x=field, y="ami", data=df, order=order, ax=axs[i]).set_ylabel("Adjusted mutual information with ground truth")

fig.tight_layout()
fig.savefig(args.summary)
