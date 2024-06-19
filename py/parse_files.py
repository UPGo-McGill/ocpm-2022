from Parser import Parser

import os

DATA_PATH = 'data/sample'
EXCEPTIONS_PATH = r'output/parse_exceptions.txt'

def print_debug(dtype:str, fn:str, idx:int):
  print(f"Starting on {dtype} {fn} at index {idx}.")
  
def print_progress(dtype:str, fn:str, idx:int):
  print(f"Processed {dtype} {fn} at index {idx}.")

exceptions = []
for idx, path in enumerate(os.scandir(DATA_PATH)):
    if path.is_file():
        fn = os.path.basename(path.path)
        if fn.startswith("8"):
          print_debug("citizen_sub", fn, idx)
          citizen_sub_parser = Parser(path)
          citizen_sub_parser.read_letter()
          try: 
            citizen_sub_parser.split_letters_reports_by_sentence()
            citizen_sub_parser.save_sents(f'sample_output/citizen_sub_{fn}')
          except AttributeError:
            exceptions.append(path)
          print_progress("citizen_sub", fn, idx)
        if fn.startswith("report"):
          print_debug("report", fn, idx)
          report_parser = Parser(path)
          report_parser.read_report()
          try:
            report_parser.split_letters_reports_by_sentence()
            report_parser.save_sents('sample_output/report')
          except AttributeError:
            exceptions.append(path)
          print_progress("report", fn, idx)
        if fn.startswith("6"):
          print_debug("hearing", fn, idx)
          hearing_parser = Parser(path)
          hearing_parser.read_hearing()
          try:
            hearing_parser.split_hearings_by_sentence()
            hearing_parser.save_sents(f'sample_output/hearing_{fn}')
          except AttributeError:
            exceptions.append(path)
          print_progress("hearing", fn, idx)

with open(EXCEPTIONS_PATH, 'w') as fp:
    fp.writelines(exceptions)