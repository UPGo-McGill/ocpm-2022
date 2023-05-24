import PyPDF2
import os
import pandas as pd
import pdftotext
import re


def read_letter_text(file_path):
    """
    Reads the text content from a PDF file and returns it as a string.
    :param file_path: The path to the PDF file to read.
    :return: A string containing the text content of the PDF.
    """
    # Open the PDF file using PyPDF2
    with open(file_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        print(pdf_reader)
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

def read_hearing_text(file_path):
  with open(REPORT_PATH, "rb") as f:
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

  # ALL OF THESE SEMI-WORK
  #pattern = r"([A-Z'-’. ][A-Z'-’. ]* :\n)(.*?)(?=\n[A-Z'-’. ][A-Z'-’. ]* :|$)"
  #pattern = r"([A-Z'-’. ][A-Z'-’. ]* ?\:)(.*?)(?=[A-Z'-’. ][A-Z'-’. ]* ?\:|$)"
  #pattern = r"([A-Z'-’. ][A-Z'-’. ]* ?\:)\s*?(.*?)(?=[A-Z'-’. ][A-Z'-’. ]* ?\:|$)"
  #pattern = r"([A-Z][A-Z'-’. ]* ?\:)\s*?(.*?)(?=[A-Z][A-Z'-’. ]* ?\:|$)"
  pattern = r"([A-Z][A-Z.][A-Z'-’. ]* ?\:)(?:\s*(.*?))(?=[A-Z][A-Z'-’. ]* ?\:|$)"
  #pattern = r"(MME|LA|M\.)\s+\w+\s+\w+:(.*?)(?=(MME|LA|M\.|$))(?<!:\s)"
  result = re.findall(pattern, pages, re.DOTALL) # Find all regex matches in the 
  
  #print(result)
  result = [(r[0].strip().replace("\n", ""), 
             r[1].strip().replace("\n", "")) 
            for r in result] 
  # Create a list of tuples with the delimiter and following text

  result = [(r[0].replace(":", "").strip(), r[1]) for r in result]
  return result

DATA_PATH = 'data/pdf_examples'

letter_file = '8.2_marielle_ouellette.pdf'
#extract text in byte format
LETTER_PATH = f'{DATA_PATH}/{letter_file}'
#letter_text = read_letter_text(LETTER_PATH)
#print(letter_text)

report_file = '7.1_ocpm_16_05_12_franciscains.pdf'
REPORT_PATH = f'{DATA_PATH}/{report_file}'
hearing_text = read_hearing_text(REPORT_PATH)
for ht in hearing_text:
  print(ht)
  print("\n")

df = pd.DataFrame(hearing_text, columns=['speaker', 'text'])
df.to_csv("data/text_report.csv")
#print(df[:4])
#report_text = read_letter_text(REPORT_PATH)
#print(report_text)