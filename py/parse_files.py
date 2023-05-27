from Parser import Parser

import os

DATA_PATH = 'data/sample'

def print_progress(dtype:str, idx:int):
  print(f"Processed {dtype} at index {idx}.")

for idx, path in enumerate(os.scandir(DATA_PATH)):
    if path.is_file():
        fn = os.path.basename(path.path)
        if fn.startswith("8"):
          citizen_sub_parser = Parser(path)
          citizen_sub_parser.read_letter()
          citizen_sub_parser.split_letters_reports_by_sentence()
          citizen_sub_parser.save_sents(f'sample_output/citizen_sub_{fn}')
          print_progress("citizen_sub", idx)
        if fn.startswith("report"):
          report_parser = Parser(path)
          report_parser.read_report()
          report_parser.split_letters_reports_by_sentence()
          report_parser.save_sents('sample_output/report')
          print_progress("report", idx)
        if fn.startswith("6"):
          hearing_parser = Parser(path)
          hearing_parser.read_hearing()
          hearing_parser.split_hearings_by_sentence()
          hearing_parser.save_sents(f'sample_output/hearing_{fn}')
          print_progress("hearing", idx)