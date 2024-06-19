import json
import os
import pandas as pd

from langchain_community.document_loaders import Docx2txtLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma

examples = json.load(open('../data/RAG_resources/examples.json', 'r'))
examples_fr = json.load(open('../data/RAG_resources/examples_fr.json', 'r'))

# RAG
loader = Docx2txtLoader("../data/RAG_resources/green_gray.docx")
gg_article = loader.load()

# Initialize RecursiveCharacterTextSplitter to make chunks of text
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

# Split text
splits = text_splitter.split_documents(gg_article)