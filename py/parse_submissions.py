
from Parser import Parser
from tqdm import tqdm
from utils import *

import os

DATA_PATH = 'data/all_submissions'
LOGS = r'output/parsed_submissions/_logs/'
EXCEPTIONS_PATH = f'{LOGS}parse_exceptions.txt'
SUCCESS_PATH = f'{LOGS}parse_successes.txt'

exceptions = []
n_dirs = len(list(os.scandir(DATA_PATH)))
dirs = os.scandir(DATA_PATH)

for dir_path in tqdm(dirs, total=n_dirs, position=0, leave=True):
    if dir_path.is_dir():
        for f_idx, f_path in enumerate(os.scandir(dir_path.path)):
            if f_path.is_file():
                dn = os.path.basename(dir_path.path).split("/")[-1]
                fn = os.path.basename(f_path.path).replace(".pdf", "")
                submissions_parser = Parser(f_path, doc_type="letter")
                submissions_parser.read_letter()
                try:
                    submissions_parser.split_letters_reports_by_sentence()
                    submissions_parser.save_sents(f'parsed_submissions/{dn}_{fn}')
                    with open(SUCCESS_PATH, 'a') as fp:
                        fp.write(f_path.path + "\n")
                except AttributeError:
                    #exceptions.append(f_path)
                    with open(EXCEPTIONS_PATH, 'a') as fp:
                        fp.write(f_path.path + "\n")

#with open(EXCEPTIONS_PATH, 'w') as fp:
#    fp.writelines(exceptions)