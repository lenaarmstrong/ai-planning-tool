import logging
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from api.routers import llm_rag_chat

logging.basicConfig(
    level=logging.DEBUG,  # Change to INFO or ERROR for less verbosity
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()  # Log to the console
    ]
)

logger = logging.getLogger(__name__)

# Setup FastAPI app
app = FastAPI(title="API Server", description="API Server", version="v1")

# Enable CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=False,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
@app.get("/")
async def get_index():
    return {"message": "Welcome to AC215"}

app.include_router(llm_rag_chat.router, prefix="/api", tags=["RAG"])
