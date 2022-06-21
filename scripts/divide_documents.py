import argparse
import xml.etree.ElementTree as etree
import json
import re
from nltk.tokenize import word_tokenize

parser = argparse.ArgumentParser()
parser.add_argument("--primary_source", dest="primary_source")
parser.add_argument("--subdocuments", dest="subdocuments")
parser.add_argument("--words_per_subdocument", dest="words_per_subdocument", type=int)
args = parser.parse_args()

results = {"file" : args.primary_source, "subdocuments" : []}
if args.primary_source.endswith("tei"):
    with open(args.primary_source, "rt") as ifd:
        xml = etree.parse(ifd)
        title = xml.find(".//{*}titleStmt/{*}title").text
        author_element = xml.find(".//{*}author")
        pers_element = author_element.find(".//{*}persName") if author_element else None
        author_name_components = list(pers_element.itertext() if pers_element else author_element.itertext() if author_element else ["Anonymous"])
        author = re.sub(r"\s+", " ", " ".join(author_name_components)).strip()
        results["author"] = author
        results["title"] = title
        current_doc = []
        for paragraph in xml.findall(".//{*}text//{*}p"):
            paragraph_contents = " ".join(list(paragraph.itertext())).strip()
            for word in word_tokenize(paragraph_contents):
                current_doc.append(word)
                if len(current_doc) == args.words_per_subdocument:
                    results["subdocuments"].append(current_doc)
                    current_doc = []
        if len(current_doc) > 0:
            results["subdocuments"].append(current_doc)
else:
    raise Exception("The input document '{}' does not appear to be in a recognized format (either the extension is unknown, or you need to add handling logic for it to 'scripts/divide_documents.py')".format(args.source_document))
    
with open(args.subdocuments, "wt") as ofd:
    ofd.write(json.dumps(results, indent=4))
