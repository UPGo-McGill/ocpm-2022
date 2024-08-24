import json
import os
import pandas as pd
import sys

from dotenv import load_dotenv

from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain_community.document_loaders import Docx2txtLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from tqdm import tqdm

from prompt_utils import (return_RAG_chain, 
                          return_chain, 
                          pipe, 
                          add_RAG_output_to_data)
from sampling_utils import sample_sents_for_RAG, RAG_outputs_to_jsonl

# Set environment variables and file paths
RAG_PATH = 'data/RAG_resources/'
RAG_OUT_PATH = 'output/RAG_samples/'
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Sample sentences
sample_name = sys.argv[1]
sample_size = 0.005
sampled_sents = sample_sents_for_RAG(sample_frac=sample_size)
print(sampled_sents)

# Examples for debugging
# examples = json.load(open(f'{RAG_PATH}examples.json', 'r'))

# Load RAG templates
with open(f'{RAG_PATH}sus_template.txt', 'r') as f:
    sus_template = f.read()
    
with open(f'{RAG_PATH}gg_template.txt', 'r') as f:
    gg_template = f.read()
    
with open(f'{RAG_PATH}climate_template.txt', 'r') as f:
    climate_template = f.read()

# Load RAG external resource
loader = Docx2txtLoader(f'{RAG_PATH}green_gray.docx')
gg_article = loader.load()

# Initialize RecursiveCharacterTextSplitter to make chunks of text
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

# Split text
splits = text_splitter.split_documents(gg_article)

# Initialize Chroma vectorstore with documents as splits and using OpenAIEmbeddings
vectorstore = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings())

# Setup vectorstore as retriever
retriever = vectorstore.as_retriever()

# Initialize LLM
llm = ChatOpenAI(model_name="gpt-4o", temperature=0.7).bind(logprobs=True)

# Initialize LLM and RAG chains
sus_chain = return_RAG_chain(sus_template, retriever, llm)
gg_chain = return_RAG_chain(gg_template, retriever, llm)
climate_chain = return_chain(climate_template, llm)

print(f"Running RAG queries for {sampled_sents.shape[0]} samples.")

# Loop over sampled sentences
RAG_outputs = []
for sent in tqdm(sampled_sents['sentence']):
    RAG_outputs.append(
        pipe(sent, sus_chain, gg_chain, climate_chain))

# Merge RAG outputs with sampled sentences
sample_with_RAG = add_RAG_output_to_data(sampled_sents, RAG_outputs)

# Save output
RAG_outputs_to_jsonl(sample_df=sample_with_RAG,
                     name=sample_name)