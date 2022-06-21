import logging
import gzip
import argparse
import json
from nltk.corpus import stopwords

parser = argparse.ArgumentParser()
parser.add_argument("--input", dest="input")
parser.add_argument("--representations", dest="representations")
#parser.add_argument("--stem", dest="stem", default=False, action="store_true")
parser.add_argument("--minimum_count", dest="minimum_count", default=1)
parser.add_argument("--number_of_words", dest="number_of_words", type=int, default=200)
parser.add_argument("--method", dest="method", choices=["stopwords", "frequency"], default="stopwords")
args = parser.parse_args()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")

def frequency_based_list(fname, number_of_words):
    document_frequencies = {}
    author_frequencies = {}
    title_frequencies = {}
    total_document_count = 0
    unique_authors = set()
    unique_titles = set()
    with gzip.open(fname, "rt") as ifd:
        for i, line in enumerate(ifd):
            logging.info("Processing document #%d", i + 1)
            j = json.loads(line)
            unique_authors.add(j["author"])
            unique_titles.add(j["title"])
            total_document_count += 1
            for word in j["features"].keys():
                document_frequencies[word] = document_frequencies.get(word, 0) + 1
                #author_frequencies[word] = author_frequencies.get(word, set())
                #author_frequencies[word].add(j["author"])
    scored_words = []
    for word, document_count in document_frequencies.items():
        scored_words.append((document_count / total_document_count, word))
        #scored_words.append((document_count / total_document_count + author_frequencies[word] / len(unique_authors), word))
    top_words = sorted(scored_words, reverse=True)[0:number_of_words]
    return [w for _, w in top_words]

word_list = stopwords.words("english") if args.method == "stopwords" else frequency_based_list(args.input, args.number_of_words)
logging.info("Chose top %d words", len(word_list))

with gzip.open(args.input, "rt") as ifd, gzip.open(args.representations, "wt") as ofd:
    for i, line in enumerate(ifd):
        logging.info("Processing document #%d", i + 1)
        j = json.loads(line)
        item = {
            "author" : j["author"],
            "title" : j["title"],
            "birth_year" : j["birth_year"],
            "death_year" : j["death_year"],
            "representation" : {},
        }
        total = sum(j["features"].values())
        for word, count in [(k, v) for k, v in j["features"].items() if k in word_list]:
            item["representation"][word] = count / total
        ofd.write(json.dumps(item) + "\n")

