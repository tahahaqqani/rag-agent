from typing import List, Dict, Any
import os
import logging

from langchain_chroma import Chroma
from langchain.docstore.document import Document
from FlagEmbedding import FlagReranker
from langchain_huggingface import HuggingFaceEmbeddings

# Get logger from package
logger = logging.getLogger(__name__)

# Embeddings (BGE small - good balance of quality and speed)
EMBED_MODEL_NAME = os.getenv("EMBED_MODEL", "BAAI/bge-small-en-v1.5")

# Create / load vector store
CHROMA_DIR = os.getenv("CHROMA_DIR", "./chroma_db")
COLLECTION_NAME = os.getenv("COLLECTION", "docs")

# Initialize embeddings with normalization for better similarity search
embeddings = HuggingFaceEmbeddings(
    model_name=EMBED_MODEL_NAME, 
    encode_kwargs={"normalize_embeddings": True}
)

# Lazy-init Chroma store (collections auto-created on first add)
vectorstore = Chroma(
    collection_name=COLLECTION_NAME, 
    embedding_function=embeddings, 
    persist_directory=CHROMA_DIR
)

# Local reranker (cross-encoder) for improving retrieval quality
reranker = FlagReranker(os.getenv("RERANK_MODEL", "BAAI/bge-reranker-base"))

logger.info(f"RAG pipeline initialized with model: {EMBED_MODEL_NAME}")
logger.info(f"Vector store: {CHROMA_DIR}")
logger.info(f"Collection: {COLLECTION_NAME}")


def retrieve(query: str, k: int = 8) -> List[Dict[str, Any]]:
    """
    Dense retrieval via Chroma, then rerank with cross-encoder.
    
    Args:
        query: User's question
        k: Number of documents to retrieve initially
        
    Returns:
        List of dicts with: {text, metadata, score, rerank_score}
    """
    try:
        # Step 1: Dense retrieval using embeddings
        docs_and_scores = vectorstore.similarity_search_with_score(query, k=k)
        
        if not docs_and_scores:
            logger.warning(f"No documents found for query: {query}")
            return []
        
        # Step 2: Prepare pairs for reranking
        pairs = [(query, doc.page_content) for doc, _ in docs_and_scores]
        
        # Step 3: Rerank using cross-encoder for better relevance
        rerank_scores = reranker.compute_score(pairs)
        
        # Step 4: Combine and sort results
        items = []
        for (doc, sim_score), rr_score in zip(docs_and_scores, rerank_scores):
            items.append({
                "text": doc.page_content,
                "metadata": doc.metadata,
                "score": float(sim_score),  # Similarity score from embeddings
                "rerank_score": float(rr_score)  # Reranking score from cross-encoder
            })
        
        # Sort by rerank score (higher is better)
        items.sort(key=lambda x: x["rerank_score"], reverse=True)
        
        logger.info(f"Retrieved {len(items)} documents for query: {query}")
        return items
        
    except Exception as e:
        logger.error(f"Error in retrieval: {str(e)}")
        return []


def get_collection_info() -> Dict[str, Any]:
    """Get information about the current vector collection."""
    try:
        collection = vectorstore._collection
        if collection:
            count = collection.count()
            return {
                "document_count": count,
                "collection_name": COLLECTION_NAME,
                "embedding_model": EMBED_MODEL_NAME
            }
        return {"error": "Collection not initialized"}
    except Exception as e:
        logger.error(f"Error getting collection info: {str(e)}")
        return {"error": str(e)}


def clear_collection():
    """Clear all documents from the collection."""
    try:
        vectorstore._collection.delete(where={})
        vectorstore.persist()
        logger.info("Collection cleared successfully")
        return {"success": True, "message": "Collection cleared"}
    except Exception as e:
        logger.error(f"Error clearing collection: {str(e)}")
        return {"success": False, "error": str(e)}
