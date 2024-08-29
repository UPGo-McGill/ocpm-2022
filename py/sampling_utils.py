import copy
import json
import numpy as np
import pandas as pd

from typing import Dict, List

LOG_FN = "output/logs/RAG_sampled_indexes.txt"
LOG_SENT_FN = "output/logs/RAG_sampled_sents.txt"
SENT_FN = "output/all_sentences.csv"

def append_sample_log(data, log_fn:str=LOG_FN):
    with open(log_fn, 'a') as file: 
        file.write(data + '\n') 

def load_sents(fn:str=SENT_FN):
    all_sents = pd.read_csv(fn).reset_index().drop(
        ["Unnamed: 0.1", "Unnamed: 0"], axis=1
    )
    all_sents = all_sents.rename(columns={"index": "idx"})
    all_sents['idx'] = all_sents['idx'].astype(str)
    return all_sents

def filter_away_short_sentences(all_sents:pd.DataFrame, sent_len:int=299) -> pd.DataFrame:
    mask = (all_sents['sentence'].str.len() > sent_len)
    long_sents = all_sents[mask].copy().sample(frac=1).reset_index(drop=True)
    return long_sents

def set_prob_columns(sampled_sents:pd.DataFrame) -> pd.DataFrame:
    sampled_sents["gg_prob"] = np.nan
    sampled_sents["climate_prob"] = np.nan
    return sampled_sents

def sample_sents_for_RAG(fn:str=SENT_FN,
                         log_fn:str=LOG_FN,
                         sample_frac:float=0.001,
                         filter_short:bool=True):
    all_sents = load_sents(SENT_FN)
    if filter_short:
        filter_away_short_sentences(all_sents)
    RAG_sampled = open(log_fn, "r").readlines()
    all_sents = all_sents.loc[~all_sents['idx'].isin(RAG_sampled)]
    sampled_sents = all_sents.groupby('type').apply(
        lambda x: x.sample(frac=sample_frac))
    sampled_sents = set_prob_columns(sampled_sents)
    for idx, row in sampled_sents.iterrows():
        append_sample_log(row['idx'], LOG_FN)
        append_sample_log(row['sentence'], LOG_SENT_FN)
    return sampled_sents.reset_index(drop=True)

def RAG_outputs_to_csv(sample_df:pd.DataFrame,
                     name:str,
                     ROOT:str= f"output/RAG_samples/"):
    sample_df.to_csv(f"output/RAG_samples/{name}")

def df_to_batches(df:pd.DataFrame, n:int=10) -> List[pd.DataFrame]:
    list_df = [df[i:i+n] for i in range(0, copy.deepcopy(df).shape[0],n)]
    return list_df

def RAG_outputs_to_jsonl(idx:int,
                         sample_df:pd.DataFrame,
                         name:str):
    to_jsonl = []
    for idx, row in sample_df.iterrows():
        item = process_item(row)
        to_jsonl.append(item)
    if idx == 0:
        write_mode = 'w'
    else:
        write_mode = 'a'
        
    with open(f"output/RAG_samples/{name}", write_mode) as f:
        for item in to_jsonl:
            f.write(json.dumps(item) + "\n")

def climate_to_label(label:str)->str:
    return 'climate' if label=='yes' else 'other'

def gg_to_label(label:str)->str:
    return 'other' if label=='no' else label
    
def process_item(row:Dict) -> Dict:
    item = {}
    sentence_no_fr = fr_to_non_fr(row['sentence'])
    item['text'] = row['sentence']
    item['meta'] = {}
    item['meta']['text_no_fr'] = sentence_no_fr
    item['meta']['Green_Grey'] = row['gg']
    item['meta']['GG_prob'] = np.round(row['gg_prob'], 2)
    item['meta']['Climate'] = row['climate']
    item['meta']['Climate_prob'] = np.round(row['climate_prob'], 2)
    item['meta']['File'] = row['file']
    item['meta']['Speaker'] = row['speaker']
    item['meta']['Lang'] = row['lang']
    item['meta']['LLM_selection'] = \
        list(
            set([
                gg_to_label(row['gg']).upper(),
                climate_to_label(row['climate']).upper()
            ])
        )
    item['accept'] = item['meta']['LLM_selection']
    return item

def fr_to_non_fr(input_txt):
    translation_table = str.maketrans("éàèùâêîôûç", "eaeuaeiouc")
    return input_txt.translate(translation_table)

#sampled_sents = sample_sents_for_RAG()
#print(sampled_sents.reset_index(drop=True))