'''
Deprecated
Exemplary version of haystack question answering on some of the Taschenhirn (flat files)
https://github.com/deepset-ai/haystack

# Note: Running this file loads a >1gb Bert based model from s3 which needs to be unpacked and stored under "model"


'''

from pathlib import Path
from fastapi import FastAPI, HTTPException


import logging

from haystack import Finder
from haystack.database import app
from haystack.reader.farm import FARMReader
from haystack.retriever.tfidf import TfidfRetriever
from haystack.indexing.io import write_documents_to_db, fetch_archive_from_http
from haystack.indexing.cleaning import clean_wiki_text

from pydantic import BaseModel
from typing import List, Dict
import uvicorn

# uncomment to load model!
#fetch_archive_from_http(url="https://s3.eu-central-1.amazonaws.com/deepset.ai-farm-models/0.3.0/bert-english-qa-large.tar.gz", output_dir="model")
#reader = FARMReader(model_dir="model/bert-english-qa-large", use_gpu=False)


## Initalize Reader, Retriever & Finder

# A retriever identifies the k most promising chunks of text that might contain the answer for our question
# Retrievers use some simple but fast algorithm, here: TF-IDF

# A reader scans the text chunks in detail and extracts the k best answers
# Reader use more powerful but slower deep learning models, here: a BERT QA model trained via FARM on Squad 2.0

logger = logging.getLogger(__name__)

#TODO Enable CORS

MODELS_DIRS = ["model"]
USE_GPU = False
BATCH_SIZE = 16

from haystack.database import db
db.create_all()

# Let's first get some documents that we want to query
# Here: 517 Wikipedia articles for Game of Thrones
doc_dir = "../data"
# Note: requires changing the function in io.py and adding encoding='utf-8' in our case
write_documents_to_db(document_dir=doc_dir, clean_func=clean_wiki_text) # , only_empty_db=True



app = FastAPI(title="Haystack API for Taschenhirn", version="0.1")

#############################################
# Load all models in memory

#############################################
## Indexing & cleaning documents
# Init a database (default: sqllite)


model_paths = []
for model_dir in MODELS_DIRS:
    path = Path(model_dir)
    if path.is_dir():
        models = [f for f in path.iterdir() if f.is_dir()]
        model_paths.extend(models)
#model_paths = [Path('./model')]

if len(model_paths) == 0:
    logger.error(f"Could not find any model to load. Checked folders: {MODELS_DIRS}")

retriever = TfidfRetriever()
FINDERS = {}
for idx, model_dir in enumerate(model_paths, start=1):
    reader = FARMReader(model_dir=str(model_dir), batch_size=BATCH_SIZE, use_gpu=USE_GPU)
    FINDERS[idx] = Finder(reader, retriever)
    logger.info(f"Initialized Finder (ID={idx}) with model '{model_dir}'")

logger.info("Open http://127.0.0.1:8000/docs to see Swagger API Documentation.")
logger.info(""" Or just try it out directly: curl --request POST --url 'http://127.0.0.1:8000/finders/1/ask' --data '{"question": "Who is the father of Arya Starck?"}'""")

#############################################
# Basic data schema for request & response
#############################################

# imho bad name "Request" -> conflicting with starlette(?) request. Hence, renaming
class Request(BaseModel):
    question: str
    filters: Dict[str, str] = None
    top_k_reader: int = 5
    top_k_retriever: int = 10

# answer before ongoing change in module haystack
class Answer(BaseModel):
    answer: str
    context: str

#class Answer(BaseModel):
#    answer: str
#    score: float = None
#    probability: float = None
#    context: str
#    offset_start: int
#    offset_end: int
#    document_id: str = None


class Response(BaseModel):
    question: str
    answers: List[Answer]






#############################################
# Endpoints
#############################################
@app.post("/finders/{finder_id}/ask", response_model=Response, response_model_exclude_unset=True)
def ask(finder_id: int, request: Request):
    finder = FINDERS.get(finder_id, None)
    if not finder:
        raise HTTPException(status_code=404, detail=f"Couldn't get Finder with ID {finder_id}. Available IDs: {list(FINDERS.keys())}")

    results = finder.get_answers(
        question=request.question, top_k_retriever=request.top_k_retriever,
        top_k_reader=request.top_k_reader, filters=request.filters
    )

    return results[0]


#if __name__ == "__main__":
#    uvicorn.run(app, host="0.0.0.0", port=8000)