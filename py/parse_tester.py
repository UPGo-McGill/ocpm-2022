from Parser import Parser

DATA_PATH = 'data/pdf_examples'

letter_file = '8.2_marielle_ouellette.pdf'
hearing_file = '7.1_ocpm_16_05_12_franciscains.pdf'
report_file = 'rapport-domaine-franciscains.pdf'

LETTER_PATH = f'{DATA_PATH}/{letter_file}'
HEARING_PATH = f'{DATA_PATH}/{hearing_file}'
REPORT_PATH = f'{DATA_PATH}/{report_file}'

hp = Parser(HEARING_PATH, 'hearings')
hp.read_hearing()
hp.split_hearings_by_sentence()
hp.save_sents('hearings')
print(hp.speaker_text)

lp = Parser(LETTER_PATH, 'letters')
lp.read_letter()
lp.split_letters_reports_by_sentence()
lp.save_sents('letters')

#print(lp.pages)

rp = Parser(REPORT_PATH, 'reports')
rp.read_report()
rp.split_letters_reports_by_sentence()
rp.save_sents('reports')

print(rp.pages)