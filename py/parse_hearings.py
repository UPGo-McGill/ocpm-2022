import copy
from Parser import Parser
from tqdm import tqdm
from utils import *

import os

DATA_PATH = 'data/all_transcripts'
EXCEPTIONS_PATH = r'output/hearings/parse_exceptions.txt'

exceptions = []
n_dirs = len(list(os.scandir(DATA_PATH)))
dirs = os.scandir(DATA_PATH)

for dir_path in tqdm(dirs, total=n_dirs, position=0, leave=True):
    if dir_path.is_dir():
        for f_idx, f_path in enumerate(os.scandir(dir_path.path)):
            if f_path.is_file():
                dn = os.path.basename(dir_path.path).split("/")[-1]
                fn = os.path.basename(f_path.path).replace(".pdf", "")
                #print_debug("hearing", fn, idx_path)
                hearing_parser = Parser(f_path, doc_type="hearing")
                hearing_parser.read_hearing()
                try:
                    hearing_parser.split_hearings_by_sentence()
                    hearing_parser.save_sents(f'/hearings/{dn}_{fn}')
                except AttributeError:
                    exceptions.append(path)
                #print_progress("hearing", fn, idx_path)

with open(EXCEPTIONS_PATH, 'w') as fp:
    fp.writelines(exceptions)