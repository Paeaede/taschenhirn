'''
New qna approach using Haystack version 0.8.0 and German Squad model

'''
from haystack.preprocessor.cleaning import clean_wiki_text
from haystack.preprocessor.utils import convert_files_to_dicts, fetch_archive_from_http
from haystack.reader.transformers import TransformersReader
from haystack.retriever.sparse import ElasticsearchRetriever
from haystack.pipeline import ExtractiveQAPipeline
from haystack.utils import print_answers
from haystack.document_store.elasticsearch import ElasticsearchDocumentStore


doc_dir = "./data"

# Convert files to dicts
# You can optionally supply a cleaning function that is applied to each doc (e.g. to remove footers)
# It must take a str as input, and return a str.
dicts = convert_files_to_dicts(dir_path=doc_dir, clean_func=clean_wiki_text, split_paragraphs=True)
# Let's have a look at the first 3 entries:
print(dicts[:3])




# Connect to Elasticsearch
document_store = ElasticsearchDocumentStore(host="localhost", username="", password="", index="taschenhirn")

# Now, let's write the dicts containing documents to our DB.
document_store.write_documents(dicts)

# initialize sparse retriever:
retriever = ElasticsearchRetriever(document_store=document_store)

# Alternative:
reader = TransformersReader(model_name_or_path="Sahajtomar/GELECTRAQA", tokenizer="Sahajtomar/GELECTRAQA")

# initialize pipe
pipe = ExtractiveQAPipeline(reader, retriever)


# You can configure how many candidates the reader and retriever shall return
# The higher top_k_retriever, the better (but also the slower) your answers.
#prediction = pipe.run(query="Welche Staaten grenzen an den Bodensee?", top_k_retriever=10, top_k_reader=5)
pipe.run(query="Welches ist der größte See Bayerns?", top_k_retriever=5, top_k_reader=2)

pipe.run(query="Wie weit erstreckt sich die Arktis?", top_k_retriever=5, top_k_reader=2)

pipe.run(query="Wie viele Planeten kreisen um die Sonne?", top_k_retriever=5, top_k_reader=2)



# EOF