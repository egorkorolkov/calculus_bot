import pdfplumber
import re
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS


def extract_text(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    return text

def clean_text(raw_text):
    text = raw_text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def split_text_into_chunks(cleaned_text, chunk_size=2000, chunk_overlap=50):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    documents = text_splitter.create_documents([cleaned_text])
    return documents


PDF_PATH = '/Users/macbook/Desktop/python_dev/RAG-pipeline/data/2014_Redkozubov.pdf'
SAVE_PATH = 'models/faiss_index'


def main():
    raw_text = extract_text(PDF_PATH)
    cleaned_text = clean_text(raw_text)
    documents = split_text_into_chunks(cleaned_text)

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vector_store = FAISS.from_documents(documents, embeddings)
    vector_store.save_local(SAVE_PATH)


if __name__ == '__main__':
    main()