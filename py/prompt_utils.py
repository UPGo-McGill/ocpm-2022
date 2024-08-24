from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables.base import RunnableSequence

from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

# Create function to make sure retriever has access to all docs
def join_docs(docs:list):
    return " ".join(doc.page_content for doc in docs)

def return_RAG_chain(template, retriever, llm):
    prompt = PromptTemplate(input_variables=['sentence', 'context'], template=template)
    chain = ({"context": retriever | join_docs, "sentence": RunnablePassthrough()}
             | prompt 
             | llm)
    return chain

def return_chain(template, llm):
    prompt = PromptTemplate(input_variables=['sentence'],template=template)
    chain = (prompt 
             | llm)
    return chain

def get_ai_message_prob(message):
    return np.exp(message.response_metadata["logprobs"]["content"][0]['logprob'])

def get_ai_message_str(message):
    return message.content.lower().strip()

def pipe(sentence:str, 
         sus_chain:RunnableSequence, 
         gg_chain:RunnableSequence,
         climate_chain:RunnableSequence) -> Tuple[Tuple[str,float], Tuple[str,float]]:
    
    sus = sus_chain.invoke(sentence)
    sus_str = get_ai_message_str(sus)
    sus_prob = get_ai_message_prob(sus)
    
    climate = climate_chain.invoke(sentence)
    climate_str = get_ai_message_str(climate)
    climate_prob = get_ai_message_prob(climate)

    if "yes" in sus.content.lower():
        gg = gg_chain.invoke(sentence)
        gg_str = get_ai_message_str(gg)
        gg_prob = get_ai_message_prob(gg)
        
        return [(gg_str, gg_prob),
                (climate_str, climate_prob)]
    else:
        return [(sus_str, sus_prob),
                (climate_str, climate_prob)]

def add_RAG_output_to_data(sample_df:pd.DataFrame, llm_outputs:List[Tuple[str,str]]):
    sample_df["gg"] = [op[0][0] for op in llm_outputs]
    sample_df["climate"] = [op[1][0] for op in llm_outputs]
    
    sample_df["gg_prob"] = [op[0][1] for op in llm_outputs]
    sample_df["climate_prob"] = [op[1][1] for op in llm_outputs]
    
    return sample_df

