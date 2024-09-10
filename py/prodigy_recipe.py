from pathlib import Path

from prodigy.core import Arg, recipe
from prodigy.components.preprocess import add_tokens
from prodigy.components.stream import get_stream

import prodigy
import spacy

@prodigy.recipe(
    "green_grey_climate",
    dataset=Arg(help="Dataset to save answers to."),
    file_path=Arg(help="Path to texts")
)
def green_grey_climate(dataset: str, file_path: Path, lang:str="en"):
    """Annotate the sentiment of texts using different mood options."""
    blocks = [
        {"view_id": "ner_manual"},
        {"view_id": "choice", "text":None},
        {"view_id": "text_input", "field_rows": 1, "field_label": "Notes"}
    ]
    
    nlp = spacy.blank(lang) 
    
    stream = get_stream(file_path) # load in the JSONL file
    stream.apply(add_tokens, nlp=nlp, stream=stream)  # tokenize the stream for ner_manual
    stream = add_options(stream)   # add options to each task
    
    return {
        "dataset": dataset,   # save annotations in this dataset
        "view_id": "blocks",  # use the choice interface
        "stream": stream,
        "config":{"blocks": blocks, "labels": ["IRRELEVANT"]}
    }

def add_options(stream):
    # Helper function to add options to every task in a stream
    
    options = [
        {"id": "green", "text": "Green"},
        {"id": "grey", "text": "Grey"},
        {"id": "climate", "text": "Climate"},
    ]
    for task in stream:
        task["options"] = options
        yield task