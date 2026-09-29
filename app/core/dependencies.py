import os
from google.oauth2 import service_account
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_qdrant import QdrantVectorStore

from app.core.settings import settings

# --- Centralized Dependencies ---

# 1. Language and Embedding Models
llm: ChatGoogleGenerativeAI
embeddings: GoogleGenerativeAIEmbeddings

# Check for Service Account first
if settings.SERVICE_ACCOUNT_FILE_PATH and os.path.exists(settings.SERVICE_ACCOUNT_FILE_PATH):
    print("Using Service Account credentials")
    creds = service_account.Credentials.from_service_account_file(
        settings.SERVICE_ACCOUNT_FILE_PATH,
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )

    llm = ChatGoogleGenerativeAI(
        model=settings.LANGUAGE_MODEL_NAME,
        project=creds.project_id,
        credentials=creds
    )

    embeddings = GoogleGenerativeAIEmbeddings(
        model=settings.EMBEDDING_MODEL_NAME,
        project=creds.project_id,
        credentials=creds
    )

# Fallback to GEMINI_API_KEY
elif settings.GEMINI_API_KEY:
    print("Using GEMINI_API_KEY")
    llm = ChatGoogleGenerativeAI(
        model=settings.LANGUAGE_MODEL_NAME,
        google_api_key=settings.GEMINI_API_KEY
    )

    embeddings = GoogleGenerativeAIEmbeddings(
        model=settings.EMBEDDING_MODEL_NAME,
        google_api_key=settings.GEMINI_API_KEY
    )

else:
    raise ValueError("No valid credentials provided. Please set either Google Cloud Service Account or GEMINI_API_KEY.")

# 3. Vector Store
vector_store = QdrantVectorStore.from_existing_collection(
    embedding=embeddings,
    collection_name=settings.QDRANT_COLLECTION_NAME,
    url=settings.QDRANT_URL,
    api_key=settings.QDRANT_API_KEY,
    timeout=60,
    https=True
)
