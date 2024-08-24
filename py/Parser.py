#!/usr/local/Caskroom/miniconda/base/envs/ocpm/bin/python

from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException
from spacy.language import Doc
from typing import List, Optional, Tuple

import os
import pandas as pd
import pdftotext
import re
import spacy

nlp_fr = spacy.load("fr_core_news_sm")
nlp_en = spacy.load("en_core_web_sm")

nlp_fr.max_length = 2500000
nlp_en.max_length = 2500000

class Parser():
    def __init__(self, PATH:str, doc_type:str):
        #self.PATH = PATH
        with open(PATH, "rb") as f:
            self.pdf = pdftotext.PDF(f)
        self.pages = ""
        self.fn = f"{doc_type}_{PATH.name.split('.')[0]}"
        #print(self.fn)
        
    def read_report(self) -> str:
        def _remove_linebreaks(pattern:str) -> str:
            # compile the regex pattern
            regex = re.compile(r'(?<=\b[a-z])\n(?=[a-z]+\b)', 
                               flags=re.IGNORECASE|re.MULTILINE)
            # substitute the matched linebreaks with a space
            expanded_pattern = regex.sub(r' ', pattern)
            return expanded_pattern
        
        def _remove_toc(page:str) -> str:
            page = re.sub(r'^(\d+\..*)\n', '', page, flags=re.M)
            page = re.sub(r'^(Annexe\s+\d+\s.*)\n', '', page, flags=re.M)
            return page

        for page in self.pdf:
            #page = re.sub(r'^\s*([0-9]+\s*)+$','\n',page, flags=re.M)
            page = re.sub(r'(\n){2,}','\r\n', page)
            page = re.sub(r'^[A-Z\d\W]+$[\r]*', '', page, flags=re.MULTILINE)
            page = re.sub(r"(?<=[a-z])\n(?=[a-z])", '', page)
            page = _remove_toc(page)
            page = re.sub(r'http\S+', '', page)
            page = _remove_linebreaks(page)
            page_lines = ""
            for line in page.splitlines():
                if not line.endswith("doc."):
                    page_lines += line + '\n'
            self.pages += page_lines
        return self.pages
    
    def read_letter(self) -> List[str]:
        """
        Reads the text content from a PDF file and returns it as a string.
        :param file_path: The path to the PDF file to read.
        :return: A string containing the text content of the PDF.
        """
        for idx, page in enumerate(self.pdf):
            page = re.sub("\t\r", '', page.encode('utf-8').decode('utf-8'))
            page = re.sub("-­‐", '-', page)
            page = " ".join(page.split())
            page = re.sub("-\\xad‐", '-', page)
            self.pages += page
        return self.pages
        
    def read_hearing(self) -> List[Tuple[str, str]]:
        for idx, page in enumerate(self.pdf):
            if idx > 2:
                page = re.sub(r'^\s*([0-9]+\s*)+$','\n',page, flags=re.M)
                page = re.sub(r'^Séance de la soirée.*\n?', '', page, flags=re.MULTILINE)
                page = re.sub(r'^Mackay Morin Maynard et associés.*\n?', '', page, flags=re.MULTILINE)
                page = page.split('FIN DE LA SOIRÉE')[0]
                page = page.split('Je, soussignée')[0]
                page = page.replace('Mme','MME')
                self.pages += page
        pattern = r"([A-Z][A-Z.][A-Z'-’. ]* ?\:)(?:\s*(.*?))(?=[A-Z][A-Z'-’. ]* ?\:|$)"
        self.speaker_text = re.findall(pattern, self.pages, re.DOTALL) # Find all regex matches in the 
        self.speaker_text = [(st[0].strip().replace("\n", ""), 
                              st[1].strip().replace("\n", "")) 
                             for st in self.speaker_text] 
        # Create a list of tuples with the delimiter and following text
        self.speaker_text = [(st[0].replace(":", "").strip(), st[1])
                             for st in self.speaker_text]
    
    def _detect_lang(self, text:str) -> Optional[str]:
        try:
            return detect(text)
        except LangDetectException:
            return None

    def _add_hearing_sentences(self, 
                               doc:Doc, 
                               lang:str, idx='') -> List[Tuple[str, str, str]]:
        doc_sents = []
        for s in doc.sents:
            if len(s) > 5:
            #if not s.text.endswith('doc.'):
            #  print(s)
                doc_sents.append((self.fn, idx, s.text, lang))
            else:
                pass
        return doc_sents

    def split_hearings_by_sentence(self):
        self.sents = []
        for h in self.speaker_text:
            lang = self._detect_lang(h[1])
            try:
                if lang == 'fr':
                    doc = nlp_fr(h[1])
                    #print(doc.text)
                    self.sents.extend(self._add_hearing_sentences(doc, lang, h[0]))
                if lang == 'en':
                    doc = nlp_en(h[1])
                    self.sents.extend(self._add_hearing_sentences(doc, lang, h[0]))
            except:
                print("No language found, sentence skipped")
                pass

    def _nlp_based_on_lang(self, text:str) -> Optional[Tuple[Doc, str]]:
        lang = self._detect_lang(text)
        if lang == 'en':
            doc = nlp_en(text)
            return doc, lang
        if lang == 'fr':
            doc = nlp_fr(text)
            return doc, lang
        else:
            return None, None
        
    def _add_letters_reports_sentences(self, 
                                       doc:Doc, 
                                       idx:str='') -> List[Tuple[str, str, str]]: 

        doc_sents = []
        for s in doc.sents:
            s, lang = self._nlp_based_on_lang(s.text)
            if s is not None:
                if len(s) > 5:
                    if not s.text.endswith('doc.'):
                        doc_sents.append((self.fn, idx, s.text, lang))
                else:
                    pass
            else:
                pass
        return doc_sents
    
    def split_letters_reports_by_sentence(self, 
                                          text_type:str='LETTER'):
        doc, _ = self._nlp_based_on_lang(self.pages)
        self.sents = self._add_letters_reports_sentences(doc, text_type)
    
    def save_sents(self, fn:str):
        #print(self.sents)
        df = pd.DataFrame(self.sents, columns=['file','speaker', 'sentence', 'lang'])
        df.to_csv(f"output/{fn}.csv")