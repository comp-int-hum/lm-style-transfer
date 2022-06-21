import gzip
import argparse
import json
import re
from sklearn.cluster import KMeans, MiniBatchKMeans, DBSCAN, AgglomerativeClustering
from sklearn import metrics
import numpy
from nltk.tokenize import wordpunct_tokenize
import xml.etree.ElementTree as etree
import sys
from datasketch import MinHash, MinHashLSH, MinHashLSHForest


parser = argparse.ArgumentParser()
parser.add_argument("--representations", dest="representations")
parser.add_argument("--cluster_count", dest="cluster_count", type=int)
parser.add_argument("--random_seed", dest="random_seed", type=int)
parser.add_argument("--clustering", dest="clustering")
parser.add_argument("--additional", dest="additional", nargs="*", default=[])
args = parser.parse_args()

mhl = MinHashLSH(threshold=0.6, num_perm=256)
mhlf = MinHashLSHForest(num_perm=256)

features = set()
docs = []
metadata = []
hashes = []
with gzip.open(args.representations, "rt") as ifd:
    for i, line in enumerate(ifd):
        #if i > 10000:
        #    break
        j = json.loads(line)
        mh = MinHash(num_perm=256)
        for w in j["title"].lower().split() + j["author"].lower().split():
            mh.update(w.encode("utf-8"))
        mhl.insert(i, mh)
        mhlf.add(i, mh)        
        docs.append(j)
mhlf.index()

to_collapse = set()
for i in range(len(docs)):
    j = docs[i]
    mh = MinHash(num_perm=256)
    for w in j["title"].lower().split() + j["author"].lower().split():
        mh.update(w.encode("utf-8"))
    #res = mhlf.query(mh, 2)
    res = frozenset([x for x in mhl.query(mh)]) # and docs[x]["title"] != docs[i]["title"]]
    to_collapse.add(res)
    
#for sims in to_collapse:
#    for i in sims:
#        print(i, docs[i]["title"])
#    print()
    #    for r in res:
    #        print(r, docs[r]["title"])
    #    print()

        
#        for k, v in j["representation"].items():
#            features.add(k)
sys.exit()
for fname in args.additional:
    with open(fname, "rt") as ifd:
        xml = etree.parse(ifd)
        title = xml.find(".//{*}titleStmt/{*}title").text
        author_element = xml.find(".//{*}author")
        pers_element = author_element.find(".//{*}persName") if author_element else None
        author_name_components = list(pers_element.itertext() if pers_element else author_element.itertext() if author_element else ["Anonymous"])
        author = re.sub(r"\s+", " ", " ".join(author_name_components)).strip()
        feats = {}
        total = 0
        
        for paragraph in xml.findall(".//{*}text//{*}p"):
            paragraph_contents = " ".join(list(paragraph.itertext())).strip()
            text = re.sub(r"\s+", " ", paragraph_contents).lower()
            for word in wordpunct_tokenize(text):
                total += 1
                if word in features:
                    feats[word] = feats.get(word, 0) + 1
        feats = {k : v / total for k, v in feats.items()}
        doc = {
            "title" : title,
            "author" : title,
            "birth_year" : 1780,
            "death_year" : 1820,
            "representation" : feats,
        }
        print(len(doc["representation"]))
        docs.append(doc)



            
feat2id = {f : i for i, f in enumerate(features)}
id2feat = {i : f for f, i in feat2id.items()}

reps = numpy.zeros(shape=(len(docs), len(features)))
for row, doc in enumerate(docs):
    for feat, val in doc["representation"].items():
        reps[row, feat2id[feat]] = val

#model = MiniBatchKMeans(n_clusters=args.cluster_count, random_state=args.random_seed, batch_size=10000)
model = DBSCAN()
model.fit(reps)

labeled = zip(model.labels_, [(d["title"], d["author"], int(d["birth_year"]) + ((int(d["death_year"]) - int(d["birth_year"])) / 2)) for d in docs])

clusters = {}
for c, info in labeled:
    clusters[c] = clusters.get(c, [])
    clusters[c].append(info)

clusters = sorted(clusters.items(), key=lambda x : len(x[1]))

with open(args.clustering, "wt") as ofd:
    for cluster_id, cluster in clusters:
        counts = {}
        for title, author, year in cluster:
            counts[author] = counts.get(author, 0) + 1
        ofd.write("Cluster #{}\n".format(cluster_id))
        for author, count in sorted(counts.items(), key=lambda x : x[1], reverse=True):
            ofd.write("{}\t{}\n".format(count, author))
        ofd.write("\n")
