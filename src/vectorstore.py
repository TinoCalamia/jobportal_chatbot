import os
import faiss
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_openai import OpenAIEmbeddings

import src.constants as con

embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
index = faiss.IndexFlatL2(len(embeddings.embed_query("hello world")))

vector_store = FAISS(
    embedding_function=embeddings,
    index=index,
    docstore=InMemoryDocstore(),
    index_to_docstore_id={},
)

def create_vectorstore_from_documents(documents, vectorstore=vector_store, embedding=OpenAIEmbeddings()):
    vector_db = vectorstore.from_documents(documents=documents, embedding=embedding)

    return vector_db

def split_documents(documents, text_splitter, chunk_size=con.SPLITTER_CHUNK_SIZE, chunk_overlap=con.SPLITTER_CHUNK_OVERLAP):
    splits = text_splitter.split_documents(documents)

    return splits

def add_documents_to_vectorstore(splitted_documents, vector_db):
    id_list = vector_db.add_documents(splitted_documents)

    return id_list