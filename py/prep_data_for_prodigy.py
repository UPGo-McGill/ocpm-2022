import json
import random

IN_ROOT = "output/RAG_samples/"
OUT_ROOT = "output/for_prodigy/"
files = ["first_4k+", "second_20k+"]

all_data = []
relevant = []
other = []
for f in files:
    print(f)
    PATH = IN_ROOT + f
    with open(PATH, "r") as infile:
        for line in infile:
            item = json.loads(line)
            del item['meta']['text_no_fr']
            if item['meta']['Green_Grey'] != 'no':
                relevant.append(item)
            elif item['meta']['Climate'] == 'yes':
                relevant.append(item)
            else:
                other.append(item)
            all_data.append(item)

print(len(all_data))
print(len(other))
print(len(relevant))

n_relevant = len(relevant)
other_sample = random.sample(other, n_relevant)
out_data = other_sample + relevant
print(len(out_data))
random.shuffle(out_data)

print(f"There are a total of {len(out_data)} items in the out file.")

for item in out_data:
    OUT_PATH = OUT_ROOT + f"first_batch_N-{n_relevant*2}.jsonl"
    with open(OUT_PATH, "a") as outfile:
        outfile.write(json.dumps(item) + "\n")
        
