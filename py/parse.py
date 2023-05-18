import PyPDF2
import os
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

DATA_PATH = 'data/pdf_examples'

letter_file = '8.2_marielle_ouellette.pdf'
#extract text in byte format
LETTER_PATH = f'{DATA_PATH}/{letter_file}'
#letter_text = read_letter_text(LETTER_PATH)
#print(letter_text)

report_file = '7.1_ocpm_16_05_12_franciscains.pdf'
REPORT_PATH = f'{DATA_PATH}/{report_file}'

import pdftotext

with open(REPORT_PATH, "rb") as f:
    pdf = pdftotext.PDF(f)

# All pages
pages = []
for idx, page in enumerate(pdf):
    #print(idx)
    #print(text)
    page = re.sub(r'^\s*([0-9]+\s*)+$','\n',page, flags=re.M)
    page = re.sub(r'^Séance de la soirée.*\n?', '', page, flags=re.MULTILINE)
    page = re.sub(r'^Mackay Morin Maynard et associés.*\n?', '', page, flags=re.MULTILINE)
    page = page.split('FIN DE LA SOIRÉE')[0]
    page = page.split('Je, soussignée')[0]
    #page = os.linesep.join([s for s in page.splitlines() if s])
    #page = page.replace("\n", " ")
    #page = page.rstrip()
    #page = page.lstrip()
    #pages += f" {page} \n"
    pages.append(page)
#rx = r"([A-Z'-’. ][A-Z'-’. ]* :\n)"
#pattern = r"([A-Z'-’. ][A-Z'-’. ]* :\n)"
pages = " ".join(pages)
#print(pages)
#print(pages)

#pattern = r"([A-Z'-’. ][A-Z'-’. ]* :\n)(.*?)(?=\n[A-Z'-’. ][A-Z'-’. ]* :|$)"
#pattern = r"([A-Z'-’. ][A-Z'-’. ]* ?\:)(.*?)(?=[A-Z'-’. ][A-Z'-’. ]* ?\:|$)"
#pattern = r"([A-Z'-’. ][A-Z'-’. ]* ?\:)\s*?(.*?)(?=[A-Z'-’. ][A-Z'-’. ]* ?\:|$)"
#pattern = r"([A-Z][A-Z'-’. ]* ?\:)\s*?(.*?)(?=[A-Z][A-Z'-’. ]* ?\:|$)"
pattern = r"([A-Z][A-Z'-’. ]* ?\:)(?:\s*(.*?))(?=[A-Z][A-Z'-’. ]* ?\:|$)"


# Find all regex matches in the string
matches = re.findall(pattern, pages, re.DOTALL)

# Create a list of tuples with the delimiter and following text
result = [(match[0], match[1]) for match in matches]

# Print the resulting list of tuples
#print(result)

# THIS KIND OF WORKED
#splitted_str = re.split(pattern, pages)
#pairs = zip(splitted_str[::2], splitted_str[1::2])
#result = [(delimiter, text) for delimiter, text in pairs]

for r in result:
  print(r)
  print("\n")

#report_text = read_letter_text(REPORT_PATH)
#print(report_text)