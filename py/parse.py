#!/usr/local/Caskroom/miniconda/base/envs/ocpm/bin/python

from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException

import PyPDF2
import os
import pandas as pd
import pdftotext
import re
import spacy

nlp_fr = spacy.load("fr_core_news_sm")
nlp_en = spacy.load("en_core_web_sm")

DATA_PATH = 'data/pdf_examples'

letter_file = '8.2_marielle_ouellette.pdf'
hearing_file = '7.1_ocpm_16_05_12_franciscains.pdf'
report_file = 'rapport-domaine-franciscains.pdf'

LETTER_PATH = f'{DATA_PATH}/{letter_file}'
HEARING_PATH = f'{DATA_PATH}/{hearing_file}'
REPORT_PATH = f'{DATA_PATH}/{report_file}'

def read_report(REPORT_PATH):
  def remove_linebreaks(pattern):
      # match a line break between consecutive lowercase words separated by whitespace
      re_pattern = r'(?<=\b[a-z])\n(?=[a-z]+\b)'

      # compile the regex pattern
      regex = re.compile(re_pattern, flags=re.IGNORECASE|re.MULTILINE)

      # substitute the matched linebreaks with a space
      expanded_pattern = regex.sub(r' ', pattern)

      return expanded_pattern
    
  def remove_toc(page):
    pattern = re.compile(r'^(\d+\..*)\n', re.M)
    page = pattern.sub('', page)
    pattern = re.compile(r'^(Annexe\s+\d+\s.*)\n', re.M)
    page = pattern.sub('', page)
    #pattern = re.compile(r'^(M\.\s\,\s.*)\n', re.M)
    #page = pattern.sub('', page)
    return page

  with open(REPORT_PATH, "rb") as f:
        pdf = pdftotext.PDF(f)

  # All pages
  pages = []
  for idx, page in enumerate(pdf):
    #page = re.sub(r'^\s*([0-9]+\s*)+$','\n',page, flags=re.M)
    page = re.sub(r'(\n){2,}','\r\n', page)
    page = re.sub(r'^[A-Z\d\W]+$[\r]*', '', page, flags=re.MULTILINE)
    page = re.sub(r"(?<=[a-z])\n(?=[a-z])", '', page)
    line_regex = re.compile("([a-z])\s\s([a-z])", flags=re.IGNORECASE|re.MULTILINE)
    page = remove_toc(page)
    page = re.sub(r'http\S+', '', page)
    page = remove_linebreaks(page)
    pages.append(page)
  return " ".join(pages)

def read_letter_text(LETTER_PATH):
    """
    Reads the text content from a PDF file and returns it as a string.
    :param file_path: The path to the PDF file to read.
    :return: A string containing the text content of the PDF.
    """
      
    # Open the PDF file using PyPDF2
    with open(LETTER_PATH, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        # Initialize an empty string to store the text content
        text_content = []
        # Iterate over each page in the PDF
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            # Extract the text content from the page
            page_text = page.extract_text()
            decoded_text = re.sub("\t\r", '', page_text.encode('utf-8').decode('utf-8'))
            decoded_text = re.sub("-­‐", '-', decoded_text)
            decoded_text = " ".join(page_text.split())
            text_content.append(decoded_text)
        # Return the text content as a string
        return text_content

def read_hearing_text(HEARING_PATH):
  with open(HEARING_PATH, "rb") as f:
      pdf = pdftotext.PDF(f)

  # All pages
  pages = []
  for idx, page in enumerate(pdf):
    #if idx < 2:
    #  print(page)
    if idx > 2:
      page = re.sub(r'^\s*([0-9]+\s*)+$','\n',page, flags=re.M)
      page = re.sub(r'^Séance de la soirée.*\n?', '', page, flags=re.MULTILINE)
      page = re.sub(r'^Mackay Morin Maynard et associés.*\n?', '', page, flags=re.MULTILINE)
      page = page.split('FIN DE LA SOIRÉE')[0]
      page = page.split('Je, soussignée')[0]
      page = page.replace('Mme','MME')
      pages.append(page)
  pages = " ".join(pages)
  pattern = r"([A-Z][A-Z.][A-Z'-’. ]* ?\:)(?:\s*(.*?))(?=[A-Z][A-Z'-’. ]* ?\:|$)"
  result = re.findall(pattern, pages, re.DOTALL) # Find all regex matches in the 
  result = [(r[0].strip().replace("\n", ""), 
             r[1].strip().replace("\n", "")) 
            for r in result] 
  # Create a list of tuples with the delimiter and following text
  result = [(r[0].replace(":", "").strip(), r[1]) for r in result]
  return result

#letter_text = read_letter_text(LETTER_PATH)
#report_text = read_report(REPORT_PATH)
hearing_tuples = read_hearing_text(HEARING_PATH)

#for ht in hearing_text:
#  print(ht)
#  print("\n")

def detect_lang(text):
  try:
    return detect(text)
  except LangDetectException:
    return None

def add_sentence(idx, doc, lang):
  doc_sents = []
  for s in doc.sents:
    doc_sents.append((idx, s, lang))
    #print(s)
    #print("\n")
  return doc_sents

def split_hearings_by_sentence(hearing_tuples):
  sents = []
  for h in hearing_tuples:
    lang = detect_lang(h[1])
    if lang == 'fr':
      doc = nlp_fr(h[1])
      sents.append(add_sentence(h[0], doc, lang))
    if lang == 'en':
      doc = nlp_en(h[1])
      sents.append(add_sentence(h[0], doc, lang))
  return sents

h_sents = split_hearings_by_sentence(hearing_tuples)
print(h_sents[:5])
df = pd.DataFrame(hearing_tuples, columns=['speaker', 'sentence'])
df.to_csv("data/text_report.csv")