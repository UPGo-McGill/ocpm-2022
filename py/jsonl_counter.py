import json
import sys

ROOT = "output/RAG_samples/"
FILE = sys.argv[1]

items = []
with open(ROOT + FILE, "r") as f:
    for line in f:
        items.append(json.loads(line))

green = 0
grey = 0
climate = 0
other = 0
for item in items:
    if item['meta']['Green_Grey']=='grey':
        grey += 1
    if item['meta']['Green_Grey']=='green':
        green += 1
    if item['meta']['Climate']=='yes':
        climate += 1
    else:
        other += 1

print(f"Green: {green}\nGreey: {grey}\nClimate: {climate}\nOther: {other}")
