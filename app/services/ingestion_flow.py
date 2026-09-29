import uuid
import tempfile
import os
from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader

from app.db.vector_store import VectorStoreManager
from app.core.dependencies import vector_store

def ingest_pdf_files(file_paths: List[str]) -> List[Document]:
    """Reads PDF files, splits them, and returns a list of Documents."""
    documents = []
    
    for file_path in file_paths:
        try:
            loader = PyPDFLoader(file_path)
            docs = loader.load()
            documents.extend(docs)
        except Exception as e:
            print(f"Error loading PDF {file_path}: {e}")
            
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150
    )
    
    final_documents = text_splitter.split_documents(documents)
    
    # Add a unique ID to each document
    for doc in final_documents:
        doc.metadata["id"] = str(uuid.uuid4())
        
    print(f"Nombre total de chunks prêts pour Qdrant : {len(final_documents)}")
    return final_documents

def insert_documents_in_vector_store(documents: List[Document]):
    """Orchestrates the ingestion of documents into the vector store."""
    if not documents:
        return []

    db_manager = VectorStoreManager(vector_store)
    inserted_ids = db_manager.insert_documents(documents)
    
    return inserted_ids
