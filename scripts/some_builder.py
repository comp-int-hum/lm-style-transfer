import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--sourceA", dest="sourceA")
parser.add_argument("--sourceB", dest="sourceB")                      
parser.add_argument("--target", dest="target")
args = parser.parse_args()
