'''
Preprocessing of data, following the approach presented under
https://github.com/deepset-ai/haystack/blob/master/tutorials/Tutorial8_Preprocessing.ipynb

and adapted to our data

'''


from haystack.file_converter.txt import TextConverter
from haystack.file_converter.pdf import PDFToTextConverter
from haystack.file_converter.docx import DocxToTextConverter

from haystack.preprocessor.utils import convert_files_to_dicts, fetch_archive_from_http
from haystack.preprocessor.preprocessor import PreProcessor

# fetch exemplary data to compare data with
doc_dir = "./data/preprocessing_tutorial"
s3_url = "https://s3.eu-central-1.amazonaws.com/deepset.ai-farm-qa/datasets/documents/preprocessing_tutorial.zip"
fetch_archive_from_http(url=s3_url, output_dir=doc_dir)

# Here are some examples of how you would use file converters

converter = TextConverter(remove_numeric_tables=True, valid_languages=["en"])
doc_txt = converter.convert(file_path="data/preprocessing_tutorial/classics.txt", meta=None)

#converter = PDFToTextConverter(remove_numeric_tables=True, valid_languages=["en"])
#doc_pdf = converter.convert(file_path="data/preprocessing_tutorial/bert.pdf", meta=None)

#converter = DocxToTextConverter(remove_numeric_tables=True, valid_languages=["en"])
#doc_docx = converter.convert(file_path="data/preprocessing_tutorial/heavy_metal.docx", meta=None)

# in our case:
converter = TextConverter(remove_numeric_tables=True, valid_languages=["de"])
doc_txt = converter.convert(file_path="./data/geschichte_19._Jahrhundert.txt", meta=None)
# TODO: Scraping is not correct yet. E.g. Code civil is incorrect (text after it is left out)

# This is a default usage of the PreProcessor.
# Here, it performs cleaning of consecutive whitespaces
# and splits a single large document into smaller documents.
# Each document is up to 1000 words long and document breaks cannot fall in the middle of sentences
# Note how the single document passed into the document gets split into 5 smaller documents

preprocessor = PreProcessor(
    clean_empty_lines=True,
    clean_whitespace=True,
    clean_header_footer=False,
    split_by="word",
    split_length=100,
    split_respect_sentence_boundary=True
)
#    clean_empty_lines will normalize 3 or more consecutive empty lines to be just a two empty lines
#    clean_whitespace will remove any whitespace at the beginning or end of each line in the text
#    clean_header_footer will remove any long header or footer texts that are repeated on each page



docs_default = preprocessor.process(doc_txt)
print(f"n_docs_input: 1\nn_docs_output: {len(docs_default)}")




# EOF