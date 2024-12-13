from fastapi import APIRouter, HTTPException
from api.utils.llm_rag_utils import download_files_from_bucket, retrieve_documents, rank_and_filter_documents, generate_answer
import vertexai
from vertexai.generative_models import GenerativeModel
import logging
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()

class QueryRequest(BaseModel):
    query: str

@router.post("/perform_rag")
async def perform_rag(request: QueryRequest):
    query = request.query  # Access the query field
    try:
        logger.info(f"Received query: {query}")

        # RAG logic remains the same...
        # persist_directory = "paper_vector_db/"
        # model_name = "sentence-transformers/all-MiniLM-L6-v2"
        project_id = "ai-research-for-good"
        location = "us-central1"
        model_id = "gemini-1.5-flash-002"
        # TOP_K = 5

        # bucket_name = "paper-rec-bucket"
        # folder_prefix = "paper_vector_db/"
        # destination_folder = "paper_vector_db"

        # download_files_from_bucket(bucket_name, folder_prefix, destination_folder)

        logger.debug("Starting document retrieval")
        # documents = retrieve_documents(query, persist_directory, model_name)

        logger.debug("Starting document ranking and filtering")
        # model = GenerativeModel(model_id)
        # top_documents = rank_and_filter_documents(query, documents, model, top_k=TOP_K)

        logger.debug("Starting answer generation")
        answer = generate_answer(query, project_id, location, model_id)

        logger.info("Perform RAG completed successfully")
        return {"query": query, "answer": answer}

    except Exception as e:
        logger.error(f"Error in perform_rag: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
