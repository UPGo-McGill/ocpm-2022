from Parser import Parser
from tqdm import tqdm

import os

DATA_PATH = 'data/all_reports'
EXCEPTIONS_PATH = r'output/parsed_reports/parse_exceptions.txt'

exceptions = []
n_dirs = len(list(os.scandir(DATA_PATH)))
dirs = os.scandir(DATA_PATH)

for dir_path in tqdm(dirs, total=n_dirs, position=0, leave=True):
    if dir_path.is_dir():
        for f_idx, f_path in enumerate(os.scandir(dir_path.path)):
            if f_path.is_file():
                dn = os.path.basename(dir_path.path).split("/")[-1]
                fn = os.path.basename(f_path.path).replace(".pdf", "")
                print(dn)
                report_parser = Parser(f_path, doc_type="report")
                report_parser.read_report()
                try:
                    report_parser.split_letters_reports_by_sentence()
                    report_parser.save_sents(f'parsed_reports/{dn}_{fn}')
                except AttributeError:
                    exceptions.append(f_path)

with open(EXCEPTIONS_PATH, 'w') as fp:
    fp.writelines(exceptions)