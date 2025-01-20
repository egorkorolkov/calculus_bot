import pdfplumber
import re
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS


def extract_text_with_pdfplumber(pdf_path):
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