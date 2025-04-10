# src/backend/ai/adapters/service.py
import os
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_core.runnables import Runnable
from langchain.globals import set_debug
from langchain_core.output_parsers import StrOutputParser
from langchain_weaviate import WeaviateVectorStore
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.chat_models import ChatOllama

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enable debug mode if specified
if os.getenv("LANGCHAIN_DEBUG", "false").lower() == "true":
    set_debug(True)

app = FastAPI(title="LangChain MCP Adapter Service")

# Initialize vector store
def init_vector_store():
    try:
        import weaviate
        client = weaviate.Client(
            url=os.getenv("WEAVIATE_URL", "http://weaviate:8080"),
        )
        
        # Initialize embedding model (use internal embedding service or local)
        if os.getenv("USE_INTERNAL_EMBEDDING", "true").lower() == "true":
            # Using internal embedding service
            from adapters.custom_embeddings import InternalEmbeddingService
            embeddings = InternalEmbeddingService(
                base_url=os.getenv("EMBEDDING_SERVICE_URL", "http://embedding-layer:9000")
            )
        else:
            # Using local embedding model
            embeddings = HuggingFaceEmbeddings(
                model_name=os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
            )
        
        # Initialize vector store
        return WeaviateVectorStore(
            client=client,
            index_name=os.getenv("WEAVIATE_INDEX", "LangChainDocs"),
            text_key="content",
            embedding=embeddings,
        )
    except Exception as e:
        logger.error(f"Failed to initialize vector store: {str(e)}")
        raise

# Initialize LLM
def init_llm():
    try:
        # Use internal LLM service or local model
        if os.getenv("USE_INTERNAL_LLM", "true").lower() == "true":
            # Using internal LLM service
            from adapters.custom_llm import InternalLLMService
            return InternalLLMService(
                base_url=os.getenv("LLM_SERVICE_URL", "http://llm-layer:5000")
            )
        else:
            # Using local LLM via Ollama
            return ChatOllama(
                model=os.getenv("LLM_MODEL", "llama3"),
                base_url=os.getenv("OLLAMA_URL", "http://ollama:11434"),
            )
    except Exception as e:
        logger.error(f"Failed to initialize LLM: {str(e)}")
        raise

# Create the chain
def get_rag_chain():
    vector_store = init_vector_store()
    llm = init_llm()
    
    retriever = vector_store.as_retriever(
        search_kwargs={"k": int(os.getenv("RAG_TOP_K", "5"))}
    )
    
    from langchain_core.prompts import ChatPromptTemplate
    
    template = """Answer the question based on the following context:
    
    {context}
    
    Question: {question}
    
    Answer:"""
    
    prompt = ChatPromptTemplate.from_template(template)
    
    chain = (
        {"context": retriever, "question": lambda x: x}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return chain

# Query model
class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    response: str

@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    try:
        chain = get_rag_chain()
        response = chain.invoke(request.query)
        return {"response": response}
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("adapters.service:app", host="0.0.0.0", port=7100, reload=True)