# src/backend/ai/adapters/ingest.py
import os
import logging
import argparse
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_weaviate import WeaviateVectorStore
from adapters.custom_embeddings import InternalEmbeddingService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Ingest documents into the vector store")
    parser.add_argument("--data-dir", type=str, required=True, help="Directory containing documents to ingest")
    args = parser.parse_args()
    
    # Load documents
    logger.info(f"Loading documents from {args.data_dir}")
    loader = DirectoryLoader(
        args.data_dir,
        glob="**/*.txt",
        loader_cls=TextLoader
    )
    documents = loader.load()
    logger.info(f"Loaded {len(documents)} documents")
    
    # Split documents
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    splits = text_splitter.split_documents(documents)
    logger.info(f"Split into {len(splits)} chunks")
    
    # Initialize embedding model
    if os.getenv("USE_INTERNAL_EMBEDDING", "true").lower() == "true":
        # Using internal embedding service
        embeddings = InternalEmbeddingService(
            base_url=os.getenv("EMBEDDING_SERVICE_URL", "http://embedding-layer:9000")
        )
    else:
        # Using local embedding model
        from langchain_community.embeddings import HuggingFaceEmbeddings
        embeddings = HuggingFaceEmbeddings(
            model_name=os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
        )
    
    # Initialize vector store
    import weaviate
    client = weaviate.Client(
        url=os.getenv("WEAVIATE_URL", "http://weaviate:8080"),
    )
    
    # Store documents
    logger.info("Storing documents in vector store")
    WeaviateVectorStore.from_documents(
        documents=splits,
        embedding=embeddings,
        client=client,
        index_name=os.getenv("WEAVIATE_INDEX", "LangChainDocs"),
        text_key="content",
    )
    
    logger.info("Documents successfully ingested")

if __name__ == "__main__":
    main()