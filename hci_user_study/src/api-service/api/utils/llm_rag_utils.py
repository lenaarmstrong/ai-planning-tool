import os
from typing import List, Dict
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import vertexai
from vertexai.generative_models import GenerativeModel
from google.cloud import storage
import logging

logger = logging.getLogger(__name__)

def download_files_from_bucket(bucket_name: str, folder_prefix: str, destination_folder: str):
    """
    Downloads files from a specified Google Cloud Storage bucket to a local destination folder.
    Args:
        bucket_name (str): The name of the GCS bucket.
        folder_prefix (str): The folder prefix in the bucket to download files from.
        destination_folder (str): The local folder to save the downloaded files.
    """
    logger.info(f"Starting download from bucket: {bucket_name}, prefix: {folder_prefix}")
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
        logger.info(f"Created destination folder: {destination_folder}")

    blobs = bucket.list_blobs(prefix=folder_prefix)
    for blob in blobs:
        relative_path = os.path.relpath(blob.name, folder_prefix)
        local_path = os.path.join(destination_folder, relative_path)
        local_folder = os.path.dirname(local_path)
        if not os.path.exists(local_folder):
            os.makedirs(local_folder)
            logger.debug(f"Created local folder: {local_folder}")
        logger.info(f"Downloading: {blob.name} -> {local_path}")
        blob.download_to_filename(local_path)
        print(f"Downloaded {blob.name} to {local_path}")
        logger.debug(f"Downloaded {blob.name} to {local_path}")

    logger.info("All files downloaded successfully.")


def retrieve_documents(query: str, persist_directory: str, model_name: str) -> List[str]:
    """
    Retrieves relevant documents from a Chroma database using similarity search.
    Args:
        query (str): The query string to search for.
        persist_directory (str): The directory where Chroma persists its database.
        model_name (str): The HuggingFace model used for embedding.
    Returns:
        List[str]: A list of relevant document snippets.
    """
    logger.info(f"Retrieving documents for query: {query}")
    hf = HuggingFaceEmbeddings(model_name=model_name)
    logger.debug(f"Using model: {model_name} with persist directory: {persist_directory}")
    db = Chroma(
        collection_name="all_manuscripts",
        embedding_function=hf,
        persist_directory=persist_directory,
    )

    results = db.similarity_search(query, k=10)
    logger.info(f"Retrieved {len(results)} results from ChromaDB")
    documents = []
    for result in results:
        source = result.metadata.get("source", "Unknown Source")
        page_content = result.page_content
        snippet = f"Source: {source}\nContent: {page_content}"
        documents.append(snippet)

    return documents

def rank_and_filter_documents(query, documents, model, top_k=5):
    # This function ranks and filters documents using the fine-tuned model.
    list_res = []

    for doc in documents:
        input_text = (
            f"""You are an expert data annotator who works on a project to connect non-profit users to technological research papers that might be relevant to the non-profit's use case
        Please rate the following research paper for its relevance to the non-profit's user query. Output "Relevant" if the paper relevant, or "Not Relevant" if the paper is not relevant.

        User query: {query}

        Paper snippet: {doc}
        """
        )

        print("Query:", query)
        print("Number of documents:", len(documents))
        print("Top K:", top_k)
        print("Model:", model)
    

        model = GenerativeModel("projects/ai-research-for-good/locations/us-central1/endpoints/8528956776635170816")
        response = model.generate_content([input_text],)
        generated_text = response.text.strip()  # Strip whitespace from response

        if generated_text.lower() == "relevant":
            print("added")
            list_res.append(doc)

        return list_res

def generate_answer(query: str, project_id: str, location: str, model_id: str) -> str:
    """
    Generates a consolidated response using a generative model on Google Vertex AI.
    Args:
        query (str): The user query.
        project_id (str): Google Cloud project ID.
        location (str): Google Cloud location.
        model_id (str): ID of the Vertex AI generative model.
    Returns:
        str: The generated response.
    """
    # logger.info(f"Generating answer for query: {query} using {len(documents)} documents")
    # documents_combined = "\n\n".join(documents)
    # logger.debug(f"Combined documents:\n{documents_combined[:500]}")  # Log the first 500 characters
    prompt = f"""
    You are an AI assistant that helps users manage their tasks by breaking them into smaller, actionable subtasks with due dates.
    Your goal is to make the task manageable and reduce the user's cognitive load by creating a structured plan.

    Here’s the user’s task:
    {query}

    Your role is to:

    Break the given task into three smaller subtasks.
    Assign a clear, logical description to each subtask.
    Distribute the subtasks evenly across the timeline, ensuring they are actionable and consider any dependencies.
    Provide the output in the following format:
    Subtask 1: [Description] - Due Date: [Date]
    Subtask 2: [Description] - Due Date: [Date]
    Subtask 3: [Description] - Due Date: [Date]
    """

    vertexai.init(project=project_id, location=location)
    model = GenerativeModel(model_id)

    response = model.generate_content(prompt)
    return response.text
