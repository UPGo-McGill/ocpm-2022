from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables.base import RunnableSequence

from typing import Tuple

# Create function to make sure retriever has access to all docs
def join_docs(docs:list):
    return " ".join(doc.page_content for doc in docs)

def return_RAG_chain(template, retriever, llm):
    prompt = PromptTemplate(input_variables=['sentence', 'context'], template=template)
    chain = ({"context": retriever | join_docs, "sentence": RunnablePassthrough()}
             | prompt 
             | llm 
             | StrOutputParser())
    return chain

def return_chain(template, llm):
    prompt = PromptTemplate(input_variables=['sentence'],template=template)
    chain = (prompt 
             | llm 
             | StrOutputParser())
    return chain

def pipe(sentence:str, 
         sus_chain:RunnableSequence, 
         gg_chain:RunnableSequence,
         climate_chain:RunnableSequence) -> Tuple[str,str]:
    sus = sus_chain.invoke(sentence)
    climate = climate_chain.invoke(sentence)
    if "yes" in sus.lower():
        return [gg_chain.invoke(sentence).lower().strip(),
                climate.lower().strip()]
    else:
        return [sus.lower().strip(),
                climate.lower().strip()]