import pandas as pd

import os
import sys

from tqdm import tqdm

folder_keys = {
    "letters":"parsed_submissions",
    "hearings":"parsed_hearings",
    "reports":"parsed_reports"
}

ROOT = "output/"
df_list = list()
exceptions = dict()
sentences = dict()

for key in folder_keys.keys():
    #DATA_PATH = f"{ROOT}{folder_keys[sys.argv[1]]}"
    DATA_PATH = f"{ROOT}{folder_keys[key]}"
    print(f"Processing {key}.")
    n_dirs = len(list(os.scandir(DATA_PATH)))
    dirs = os.scandir(DATA_PATH)
    exceptions[key] = 0
    sentences[key] = 0
    for idx, dir_path in enumerate(tqdm(dirs, total=n_dirs, position=0, leave=True)):
        try:
            df = pd.read_csv(dir_path.path)
            metadata = dir_path.path.split("/")
            df['file_key'] = metadata[2].split(".")[0]
            df['type'] = metadata[1].split("_")[1]
            df_list.append(df)
            sentences[key] += df.shape[0]
        except:
            exceptions[key] += 1
            print(dir_path.path)
    print(f"Processed a total of {idx} csvs in {key} with {sentences[key]} sentences.")
    

all_data = pd.concat(df_list)
print(all_data.head())
print(f"There were {sum(sentences.values())} sentences in total.")
print(f"The sentences were distributed as follows:")
print(sentences)

print(f"There were {sum(exceptions.values())} exceptions in total.")
print(f"The exceptions were distributed as follows:")
print(exceptions)


all_data.to_csv(f"{ROOT}all_sentences.csv")
print(all_data.shape)
