# Performing and evaluating style transfer using GPT-3

To perform the example experiments, after cloning and changing directory into this repository, run:

```
# create and activate a virtual environment:
python3 -m venv local
source local/bin/activate

# install required packages and small corpora
pip install -r requirements.txt
python -c 'import nltk; nltk.download("stopwords")'
wget www.logical-space.org/authors.zip -O data/authors.zip
unzip data/authors.zip -d data/

# use the example configuration
cp custom.py.example custom.py
```

Now you should be able to invoke the command:

```
scons -Qn
```

and see what SCons would run.  Remove the final "n" from the command to actually do so.

The main sort of contribution to this repository should be adding or modifying files under `scripts/`,
It's also possible to edit the `SConstruct` file to augment or otherwise modify the experimental
structure (i.e. build rules, how they are combined into experiments, and the set of variables that 
can influence the experiments), though it may be more practical to describe what you hope to accomplish
as an issue, rather than diving into SCons.  Most experimental settings should be exposed through
variables that can then be customized in `custom.py`, without modifying anything in this repository.
