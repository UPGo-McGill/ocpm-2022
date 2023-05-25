import pandas as pd

#from bertopic import BERTopic

files = ['letters', 'reports', 'hearings']
docs_fr = []
docs_en = []
for f in files:
  df = pd.read_csv(f'data/{f}.csv')
  docs_fr.extend(df[df.lang == 'fr'].sentence.tolist())
  docs_en.extend(df[df.lang == 'en'].sentence.tolist())
print(len(docs_fr))
print(len(docs_en))

#print(docs_fr)
#topic_model_fr = BERTopic()
#topics_fr, probs_fr = topic_model.fit_transform(docs)