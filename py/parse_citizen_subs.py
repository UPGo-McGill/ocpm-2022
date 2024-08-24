from Parser import Parser
from utils import *

import os

DATA_PATH = 'data/all_submisions'
EXCEPTIONS_PATH = r'output/parse_exceptions_citizen_subs.txt'

exceptions = []
for idx, path in enumerate(os.scandir(DATA_PATH)):
    if path.is_file():
        fn = os.path.basename(path.path)
        print(fn)
        if fn.startswith("8"):
            print_debug("citizen_sub", fn, idx)
            citizen_sub_parser = Parser(path, doc_type="citizen_sub")
            citizen_sub_parser.read_letter()
            try: 
                citizen_sub_parser.split_letters_reports_by_sentence()
                citizen_sub_parser.save_sents(f'sample_output/citizen_sub_{fn}')
            except AttributeError:
                exceptions.append(path)
            print_progress("citizen_sub", fn, idx)

with open(EXCEPTIONS_PATH, 'w') as fp:
    fp.writelines(exceptions)