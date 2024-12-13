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

        project_id = "###"
        location = "us-central1"
        model_id = "gemini-1.5-flash-002"

        logger.debug("Starting document retrieval")

        logger.debug("Starting document ranking and filtering")

        logger.debug("Starting answer generation")
        answer = generate_answer(query, project_id, location, model_id)

        logger.info("Perform RAG completed successfully")
        return {"query": query, "answer": answer}

    except Exception as e:
        logger.error(f"Error in perform_rag: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
