import os
import pandas as pd

from bertopic import BERTopic
from bertopic.representation import (
  KeyBERTInspired,
  MaximalMarginalRelevance,
  ZeroShotClassification
)

from sklearn.feature_extraction.text import CountVectorizer
from spacy.lang.fr.stop_words import STOP_WORDS as fr_stop
from spacy.lang.en.stop_words import STOP_WORDS as en_stop

vect_model_fr = CountVectorizer(stop_words=list(fr_stop))
vect_model_en = CountVectorizer(stop_words=list(en_stop))

DATA_PATH = 'data/sample_output'
representation_model = KeyBERTInspired()

docs_fr = []
docs_en = []
for idx, path in enumerate(os.scandir(DATA_PATH)):
    if path.is_file():
        fn = os.path.basename(path.path)
        df = pd.read_csv(f'{DATA_PATH}/{fn}')
        docs_fr.extend(df[df.lang == 'fr'].sentence.tolist())
        docs_en.extend(df[df.lang == 'en'].sentence.tolist())

print(f'There are {len(docs_fr)} sentences in French')
print(f'There are {len(docs_en)} sentences in English')

def fit_topic_model(lang, rm, vm, docs):
  tm = BERTopic(language=lang, 
                representation_model=rm,
                vectorizer_model=vm,
                verbose=True)
  topics, probs = tm.fit_transform(docs)
  return tm, topics, probs

def get_topic_df(tm):
  topics_df = tm.get_topic_info()
  print(topics_df)
  keywords = []
  exceptions = []
  for idx, _ in topics_df.iterrows():
    try:
      keywords.append(tm.get_topic(idx-1)[:10])
    except:
      print(f"Exception at {idx-1}")
      keywords.append([])
      exceptions.append(idx-1)
    
  topics_df['keywords'] = keywords
  return topics_df, exceptions

def get_topic_per_doc(docs, topics):
  return pd.DataFrame({"Document": docs, "Topic": topics})

print("Fitting topic model in French")
tm_fr, topics_fr, probs_fr = fit_topic_model('french', 
                                             representation_model, 
                                             vect_model_fr, 
                                             docs_fr)
print("Extracting and saving topics in French")
topics_fr_df, exceptions_fr =  get_topic_df(tm_fr)
topics_fr_df.to_csv("output/topics_fr.csv")

print(tm_fr.find_topics('durabilité'))
doc_topic_fr = get_topic_per_doc(docs_fr, topics_fr)
doc_topic_fr.to_csv("output/doc_topic_fr.csv")

print("Fitting topic model in English")
tm_en, topics_en, probs_en = fit_topic_model('english', 
                                             representation_model, 
                                             vect_model_en, 
                                             docs_en)
print("Extracting and saving topics in English")
topics_en_df, exceptions_en =  get_topic_df(tm_en)
topics_en_df.to_csv("output/topics_en.csv")

print(tm_en.find_topics('sustainability'))
doc_topic_en = get_topic_per_doc(docs_en, topics_en)
doc_topic_en.to_csv("output/doc_topic_en.csv")