"""
Main entry point for the FastAPI chat application.

This module initializes the FastAPI application, sets up the connection to the
database, configures the LangGraph workflow, and defines the chat endpoint.
"""

import logging
import os
import sys
import uuid
import tempfile
from contextlib import asynccontextmanager
from typing import List, Annotated

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from langchain_core.messages import HumanMessage
import uvicorn

from app.core.agent_manager import AgentManager
from app.schemas.chat import ChatRequest, MessageResponse
from app.schemas.ingestion import PdfIngestion
from app.services.ingestion_flow import ingest_pdf_files, insert_documents_in_vector_store
from app.db.vector_store import VectorStoreManager
from app.core.dependencies import vector_store

# --- Logger Setup ---
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format=
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Load Environment Variables ---
load_dotenv()

agent_manager = AgentManager()



# --- FastAPI Lifespan Management ---


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages the application's lifespan events for startup and shutdown.
    
    During startup, it initializes Vertex AI, creates a database connection pool,
    sets up the LangGraph checkpointer, and compiles the graph.
    The connection pool is automatically closed on shutdown.
    """
    
    await agent_manager.setup()

    yield

# --- FastAPI Application ---

api = FastAPI(lifespan=lifespan)

api.mount("/static", StaticFiles(directory="static"), name="static")


@api.get("/")
async def home():
    return FileResponse("static/index.html")

@api.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Handles chat requests by invoking the LangGraph workflow.
    
    Args:
        request: A ChatRequest object containing the user's message and thread_id.
        
    Returns:
        A dictionary containing the AI's response, the thread_id, and any sources.
    """
    try:
        # 1. Get or create a thread ID
        thread_id = request.thread_id or str(uuid.uuid4())
        logger.info(f'Request for thread "{thread_id}": {request.message}')

        # 2. Get the current state of the conversation
        current_state = await agent_manager.get_state(thread_id)
        logger.debug(f"Current state: {current_state}")
        # 3. Add the new user message to the history
        messages = current_state.get("messages", [])
        messages.append(HumanMessage(content=request.message))

        # 4. Invoke the graph with the updated message history
        inputs = {"messages": messages, "context": []}
        result = await agent_manager.invoke(inputs, thread_id)
        logger.debug(f"Final state: {result}")

        # 5. Extract the last AI response
        last_message = result["messages"][-1]

        # 6. Format sources to include page numbers if available
        sources = []
        for doc in result.get("context", []):
            source_info = {
                "source": doc.metadata.get("source"),
                "page": doc.metadata.get("page_label"),
                
            }
            sources.append(source_info)

        return MessageResponse(
            response=last_message.content,
            thread_id=thread_id,
            language=result.get("language"),
            sources=sources
        )
    except Exception as e:
        logger.error(f"Error in /chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@api.post("/add", status_code=status.HTTP_201_CREATED)
async def add_document(
    refresh: Annotated[bool, Form(description="Set to true to delete all existing vectors before ingesting.")] = False,
    file: UploadFile = File(...),
):
    """
    Adds new documents from uploaded PDF files.

    Args:
        refresh: Set to true to delete all existing vectors before ingesting.
        file: file to ingest.

    Returns:
        A dictionary with the status of the ingestion and the inserted IDs.
    """
    try:
        # Validate that all files are PDFs
        #for file in files:
        if not file.filename.lower().endswith(".pdf") or file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail=f"File {file.filename} is not a PDF.")
            logger.info(f"Adding {file.filename} PDF documents")
            
        db_manager = VectorStoreManager(vector_store)

        if refresh:
            logger.info("Refreshing vector store")
            db_manager.delete_all_documents()

        temp_file_paths = []
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        content = await file.read()
        temp_file.write(content)
        temp_file.close()
        temp_file_paths.append(temp_file.name)

        # Ingest the documents from the files
        documents = ingest_pdf_files(temp_file_paths)
        
        # Clean up temporary files
        for path in temp_file_paths:
            os.remove(path)
            
        # Update the source metadata with the original filename (without absolute path)
        original_filename = os.path.basename(file.filename)
        for doc in documents:
            if "source" in doc.metadata:
                doc.metadata["source"] = original_filename

        if not documents:
            logger.warning("No actionable data found in the documents")
            return {
                "status": "failed_or_empty",
                "message": "Les documents ont été lus mais ne contenaient aucune donnée exploitable.",
                "inserted_ids": []
            }
        
        # Insert the document into the vector store
        inserted_ids = insert_documents_in_vector_store(documents)
        logger.info(f"{len(inserted_ids)} chunks inserted successfully")
            
        return {
            "status": "success",
            "message": f"Documents traités avec succès. {len(inserted_ids)} chunks insérés.",
            "inserted_ids": inserted_ids
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Internal error during ingestion: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Erreur interne lors du traitement de l'ingestion: {str(e)}"
        )

# --- Main Execution Block ---

if __name__ == "__main__":
    # This block is for running the application locally for development.
    # It uses uvicorn to serve the FastAPI application.
    port = int(os.environ.get('PORT', 8000))
    uvicorn.run(api, host="0.0.0.0", port=port)
