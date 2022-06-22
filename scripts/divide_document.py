import argparse
import xml.etree.ElementTree as etree
import json
import re
from nltk.tokenize import word_tokenize

parser = argparse.ArgumentParser()
parser.add_argument("--document", dest="document")
parser.add_argument("--subdocuments", dest="subdocuments")
parser.add_argument("--words_per_subdocument", dest="words_per_subdocument", type=int)
args = parser.parse_args()

with open(args.document, "rt") as ifd:
    j = json.loads(ifd.read())
    current_doc = []
    result = {k : v for k, v in j.items() if k != "text"}
    result["subdocuments"] = []
    for word in word_tokenize(j["text"]):
        current_doc.append(word)
        if len(current_doc) == args.words_per_subdocument:
            result["subdocuments"].append(current_doc)
            current_doc = []
    if len(current_doc) > 0:
        result["subdocuments"].append(current_doc)
    
with open(args.subdocuments, "wt") as ofd:
    ofd.write(json.dumps(result, indent=4))
