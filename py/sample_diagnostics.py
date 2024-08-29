import json
import sys

ROOT = "output/RAG_samples/"
FILE = sys.argv[1]
PATH = ROOT + FILE

with open(PATH, "r") as f:
    for line in f:
        print(json.load(f))