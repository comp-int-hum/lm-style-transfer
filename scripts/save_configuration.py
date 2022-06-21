import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--configuration", dest="configuration")
args, rest = parser.parse_known_args()

config = {}
for i in range(int(len(rest) / 2)):
    name = rest[i * 2].lstrip("--").upper()
    val = rest[i * 2 + 1]
    config[name] = val

with open(args.configuration, "wt") as ofd:
    ofd.write(json.dumps(config))
