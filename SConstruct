import os
import steamroller
from glob import glob

vars = Variables("custom.py")
vars.AddVariables(
    ("NUM_FOLDS", "How many random folds of all experiments should be performed?", 1),
    ("WORDS_PER_SUBDOCUMENT_VALUES", "How long should each passage be that we treat as an instance to cluster?", [500, 1000, 2000]),
    ("FEATURE_SELECTION_METHOD_VALUES", "Names of the stylometric feature selection methods to test", ["stopwords"]),
    ("NUM_FEATURES_TO_KEEP_VALUES", "How many of the stylometric features to keep", [100, 200, 400]),
    ("LOWERCASE_VALUES", "Whether to convert everything to lower-case", [True, False]),
    ("EXTENSIONS", "What extensions should be included, from files under 'data/'?", ["tei"]),
)

env = Environment(
    ENV=os.environ,
    variables=vars,
    tools=[steamroller.generate],
    BUILDERS={
        "DivideDocuments" : Builder(
            action="python scripts/divide_documents.py --primary_source ${SOURCE} --subdocuments ${TARGET} --words_per_subdocument ${WORDS_PER_SUBDOCUMENT}"
        ),
        "ExtractRepresentations" : Builder(
            action="python scripts/extract_representations.py --subdocuments ${SOURCES} --representations ${TARGET} ${'--lowercase' if LOWERCASE else ''} --feature_selection_method ${FEATURE_SELECTION_METHOD} --num_features_to_keep ${NUM_FEATURES_TO_KEEP}"
        ),
        "ClusterRepresentations" : Builder(
            action="python scripts/cluster_representations.py --representations ${SOURCE} --clustering ${TARGET} --cluster_count ${CLUSTER_COUNT}"
        ),
        "SaveConfiguration" : Builder(
            action="python scripts/save_configuration.py --configuration ${TARGET} --cluster_count ${CLUSTER_COUNT} --lowercase ${LOWERCASE} --words_per_subdocument ${WORDS_PER_SUBDOCUMENT} --feature_selection_method ${FEATURE_SELECTION_METHOD} --num_features_to_keep ${NUM_FEATURES_TO_KEEP} --fold ${FOLD}"
        ),
        "CollateResults" : Builder(
            action="python scripts/collate_results.py --summary ${TARGET} ${SOURCES}"
        )
    }
)


source_documents = sum([Glob("data/*.{}".format(x)) for x in env["EXTENSIONS"]], [])
if len(source_documents) == 0:
    env.Exit("No source documents: make sure there are files underneath 'data/' that match values in the EXTENSIONS variable.")

results = []
for fold in range(1, env["NUM_FOLDS"] + 1):
    for lowercase in env["LOWERCASE_VALUES"]:
        for words_per_subdocument in env["WORDS_PER_SUBDOCUMENT_VALUES"]:
            all_subdocuments = []
            for document in source_documents:
                subdocuments = env.DivideDocuments(
                    "work/${FOLD}/${LOWERCASE}/${WORDS_PER_SUBDOCUMENT}/${SOURCE.name}.json",
                    document,
                    FOLD=fold,
                    LOWERCASE=lowercase,
                    WORDS_PER_SUBDOCUMENT=words_per_subdocument
                )
                all_subdocuments.append(subdocuments)
            for feature_selection_method in env["FEATURE_SELECTION_METHOD_VALUES"]:
                for num_features_to_keep in env["NUM_FEATURES_TO_KEEP_VALUES"]:
                    representations = env.ExtractRepresentations(
                        "work/${FOLD}/${LOWERCASE}/${WORDS_PER_SUBDOCUMENT}/${FEATURE_SELECTION_METHOD}/${NUM_FEATURES_TO_KEEP}/representations.json",
                        all_subdocuments,
                        FOLD=fold,
                        LOWERCASE=lowercase,
                        NUM_FEATURES_TO_KEEP=num_features_to_keep,
                        WORDS_PER_SUBDOCUMENT=words_per_subdocument,
                        FEATURE_SELECTION_METHOD="stopwords"
                    )
                    for cluster_count in [5, 10, 20]:
                        clustering = env.ClusterRepresentations(
                            "work/${FOLD}/${LOWERCASE}/${WORDS_PER_SUBDOCUMENT}/${FEATURE_SELECTION_METHOD}/${NUM_FEATURES_TO_KEEP}/${CLUSTER_COUNT}/clustering.json",                            
                            representations,
                            FOLD=fold,
                            LOWERCASE=lowercase,
                            NUM_FEATURES_TO_KEEP=num_features_to_keep,
                            WORDS_PER_SUBDOCUMENT=words_per_subdocument,
                            FEATURE_SELECTION_METHOD="stopwords",
                            CLUSTER_COUNT=cluster_count
                        )
                        configuration = env.SaveConfiguration(
                            "work/${FOLD}/${LOWERCASE}/${WORDS_PER_SUBDOCUMENT}/${FEATURE_SELECTION_METHOD}/${NUM_FEATURES_TO_KEEP}/${CLUSTER_COUNT}/configuration.json",
                            [],
                            FOLD=fold,
                            LOWERCASE=lowercase,
                            NUM_FEATURES_TO_KEEP=num_features_to_keep,
                            WORDS_PER_SUBDOCUMENT=words_per_subdocument,
                            FEATURE_SELECTION_METHOD="stopwords",
                            CLUSTER_COUNT=cluster_count
                        )                    
                        results.append((clustering, configuration))
summary = env.CollateResults(
    "work/summary.png",
    results
)
