from Parser import Parser

DATA_PATH = 'data/pdf_examples'

letter_file = '8.2_marielle_ouellette.pdf'
hearing_file = '7.1_ocpm_16_05_12_franciscains.pdf'
report_file = 'rapport-domaine-franciscains.pdf'

LETTER_PATH = f'{DATA_PATH}/{letter_file}'
HEARING_PATH = f'{DATA_PATH}/{hearing_file}'
REPORT_PATH = f'{DATA_PATH}/{report_file}'

hp = Parser(HEARING_PATH)
hp.read_hearing()
hp.split_hearings_by_sentence()
hp.save_sents('hearings')

lp = Parser(LETTER_PATH)
lp.read_hearing()
lp.split_hearings_by_sentence()
lp.save_sents('letters')

rp = Parser(REPORT_PATH)
rp.read_hearing()
rp.split_hearings_by_sentence()
rp.save_sents('reports')

