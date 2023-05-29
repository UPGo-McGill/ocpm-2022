import pandas as pd

from bertopic import BERTopic
from bertopic.representation import (
  KeyBERTInspired,
  MaximalMarginalRelevance,
  ZeroShotClassification
)


DATA_PATH = 'data/sample_output'
# Create your representation model
#candidate_topics = ["climate", "sustainability", "other"]
#representation_model = ZeroShotClassification(candidate_topics, model="camembert-base")
#representation_model = MaximalMarginalRelevance(diversity=0.3)
representation_model = KeyBERTInspired()

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
topic_model_fr = BERTopic(language="french", 
                          representation_model=representation_model)
topics_fr, probs_fr = topic_model_fr.fit_transform(docs_fr)

print(topic_model_fr.get_topic_info())
#for t in topic_model_fr.get_topic(0)

print(topic_model_fr.get_topic(0)[:10])