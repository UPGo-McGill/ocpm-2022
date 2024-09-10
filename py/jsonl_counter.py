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
total = 0
for item in items:
    if item['meta']['Green_Grey']!='no':
        if item['meta']['Green_Grey']=='green':
            green += 1
        elif item['meta']['Green_Grey']=='grey':
            grey += 1
    if item['meta']['Climate']=='yes':
        climate += 1
    if item['meta']['Climate']=='no' and\
       item['meta']['Green_Grey']=='no':
        other += 1
    total += 1

print(f"Green: {green}\nGrey: {grey}\nClimate: {climate}\
\nOther: {other}\nTotal {total}")
