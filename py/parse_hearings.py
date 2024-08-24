
from Parser import Parser
from tqdm import tqdm
from utils import *

import os

DATA_PATH = 'data/all_hearings'
EXCEPTIONS_PATH = r'output/parsed_hearings/parse_exceptions.txt'

exceptions = []
n_dirs = len(list(os.scandir(DATA_PATH)))
dirs = os.scandir(DATA_PATH)

#counter = 1
#while counter < 2:
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
                    hearing_parser.save_sents(f'parsed_hearings/{dn}_{fn}')
                except AttributeError:
                    exceptions.append(path)
                #counter += 1
                    #print_progress("hearing", fn, idx_path)

with open(EXCEPTIONS_PATH, 'w') as fp:
    fp.writelines(exceptions)