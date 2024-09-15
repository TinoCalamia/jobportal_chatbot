from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
import src.constants as con

import streamlit as st

def create_vectorstore_from_documents(documents, vectorstore=Chroma(), embedding=OpenAIEmbeddings()):
    vector_db = vectorstore.from_documents(documents=documents, embedding=embedding)

    return vector_db

def split_documents(documents, text_splitter, chunk_size=con.SPLITTER_CHUNK_SIZE, chunk_overlap=con.SPLITTER_CHUNK_OVERLAP):
    splits = text_splitter.split_documents(documents)

    return splits

def add_documents_to_vectorstore(splitted_documents, vector_db):
    id_list = vector_db.add_documents(splitted_documents)

    return id_list