import pandas as pd

LOG_FN = "output/logs/RAG_sampled.txt"
SENT_FN = "output/all_sentences.csv"

def append_sample_index(idx, log_fn:str=LOG_FN):
    with open(log_fn, 'a') as file: 
        file.write(idx + '\n') 

def load_sents(fn:str=SENT_FN):
    all_sents = pd.read_csv(fn).reset_index().drop(
        ["Unnamed: 0.1", "Unnamed: 0"], axis=1
    )
    all_sents = all_sents.rename(columns={"index": "idx"})
    all_sents['idx'] = all_sents['idx'].astype(str)
    return all_sents

def sample_sents_for_RAG(fn:str=SENT_FN,
                 log_fn:str=LOG_FN,
                 sample_frac:float=0.001):
    all_sents = load_sents(SENT_FN)
    RAG_sampled = open(log_fn, "r").readlines()
    all_sents = all_sents.loc[~all_sents['idx'].isin(RAG_sampled)]
    print(all_sents.head(3))
    sampled_sents = all_sents.groupby('type').apply(
        lambda x: x.sample(frac=sample_frac))
    for idx in sampled_sents['idx']:
        append_sample_index(idx)
    return sampled_sents.reset_index(drop=True)

def save_RAG_outputs():
    pass    
#sampled_sents = sample_sents_for_RAG()
#print(sampled_sents.reset_index(drop=True))