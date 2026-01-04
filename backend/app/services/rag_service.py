import os
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
import chromadb
from chromadb.config import Settings as ChromaSettings

from ..config import get_settings
from ..models.schemas import DocumentStatus, SourceReference
from .document_parser import get_document_parser
from .gemini_client import get_gemini_client


class RAGService:
    """RAG service for document storage and retrieval."""
    
    def __init__(self):
        """Initialize RAG service with ChromaDB."""
        self.settings = get_settings()
        self.parser = get_document_parser()
        
        # Ensure vectordb directory exists
        os.makedirs(self.settings.VECTORDB_DIR, exist_ok=True)
        
        # Initialize ChromaDB with persistent storage
        self.chroma_client = chromadb.PersistentClient(
            path=self.settings.VECTORDB_DIR,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        
        # Get or create the main collection
        self.collection = self.chroma_client.get_or_create_collection(
            name="study_documents",
            metadata={"description": "Study materials knowledge base"}
        )
        
        # Document metadata storage (in-memory for simplicity)
        self._documents: Dict[str, Dict[str, Any]] = {}
        self._load_existing_documents()
    
    def _load_existing_documents(self):
        """Load existing document metadata from collection."""
        try:
            # Get all unique document IDs from the collection
            results = self.collection.get()
            if results and results.get("metadatas"):
                for metadata in results["metadatas"]:
                    if metadata and "document_id" in metadata:
                        doc_id = metadata["document_id"]
                        if doc_id not in self._documents:
                            self._documents[doc_id] = {
                                "id": doc_id,
                                "filename": metadata.get("filename", "Unknown"),
                                "file_type": metadata.get("file_type", "unknown"),
                                "status": DocumentStatus.COMPLETED,
                                "chunk_count": 0,
                                "created_at": datetime.fromisoformat(
                                    metadata.get("created_at", datetime.now().isoformat())
                                ),
                            }
                            self._documents[doc_id]["chunk_count"] += 1
        except Exception:
            pass  # Collection might be empty
    
    async def add_document(
        self,
        file_path: str,
        document_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Add a document to the knowledge base.
        
        Args:
            file_path: Path to the document file
            document_id: Optional document ID
        
        Returns:
            Document metadata
        """
        doc_id = document_id or str(uuid.uuid4())
        
        # Parse document
        text, metadata = self.parser.parse(file_path)
        
        # Chunk the text
        chunks = self.parser.chunk_text(text)
        
        # Create document record
        doc_record = {
            "id": doc_id,
            "filename": metadata["filename"],
            "file_type": metadata["file_type"],
            "status": DocumentStatus.PROCESSING,
            "chunk_count": len(chunks),
            "created_at": datetime.now(),
        }
        self._documents[doc_id] = doc_record
        
        # Add chunks to ChromaDB
        chunk_ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
        chunk_metadatas = [
            {
                "document_id": doc_id,
                "filename": metadata["filename"],
                "file_type": metadata["file_type"],
                "chunk_index": i,
                "created_at": datetime.now().isoformat(),
            }
            for i in range(len(chunks))
        ]
        
        self.collection.add(
            ids=chunk_ids,
            documents=chunks,
            metadatas=chunk_metadatas,
        )
        
        # Update status
        doc_record["status"] = DocumentStatus.COMPLETED
        
        return doc_record
    
    async def search(
        self,
        query: str,
        top_k: Optional[int] = None,
        document_ids: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant chunks.
        
        Args:
            query: Search query
            top_k: Number of results to return
            document_ids: Optional filter by document IDs
        
        Returns:
            List of relevant chunks with metadata
        """
        top_k = top_k or self.settings.TOP_K_RESULTS
        
        # Build where filter if document_ids provided
        where_filter = None
        if document_ids:
            where_filter = {"document_id": {"$in": document_ids}}
        
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            where=where_filter,
        )
        
        # Format results
        search_results = []
        if results and results.get("documents"):
            for i, doc in enumerate(results["documents"][0]):
                metadata = results["metadatas"][0][i] if results.get("metadatas") else {}
                distance = results["distances"][0][i] if results.get("distances") else 0
                
                # Convert L2 distance to similarity score
                # ChromaDB default uses L2 (squared Euclidean) distance
                # Formula: similarity = 1 / (1 + distance) gives range [0, 1]
                similarity = 1.0 / (1.0 + distance)
                
                search_results.append({
                    "text": doc,
                    "document_id": metadata.get("document_id", ""),
                    "filename": metadata.get("filename", "Unknown"),
                    "chunk_index": metadata.get("chunk_index", 0),
                    "relevance_score": similarity,
                })
        
        return search_results
    
    async def answer_question(
        self,
        question: str,
        document_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Answer a question using RAG.
        
        Args:
            question: User's question
            document_ids: Optional filter by document IDs
        
        Returns:
            Answer with sources
        """
        # Search for relevant context
        search_results = await self.search(
            query=question,
            document_ids=document_ids,
        )
        
        if not search_results:
            return {
                "answer": "抱歉，我在知识库中没有找到相关信息。请确保已上传相关文档。",
                "sources": [],
            }
        
        # Build context from search results
        context_parts = []
        for i, result in enumerate(search_results, 1):
            context_parts.append(
                f"[来源 {i}: {result['filename']}]\n{result['text']}"
            )
        context = "\n\n---\n\n".join(context_parts)
        
        # Generate answer using Gemini
        gemini = get_gemini_client()
        answer = await gemini.generate_with_context(question, context)
        
        # Format sources
        sources = [
            SourceReference(
                document_id=r["document_id"],
                document_name=r["filename"],
                chunk_text=r["text"][:200] + "..." if len(r["text"]) > 200 else r["text"],
                relevance_score=r["relevance_score"],
            )
            for r in search_results
        ]
        
        return {
            "answer": answer,
            "sources": sources,
        }
    
    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get document by ID."""
        return self._documents.get(document_id)
    
    def list_documents(self) -> List[Dict[str, Any]]:
        """List all documents."""
        return list(self._documents.values())
    
    async def delete_document(self, document_id: str) -> bool:
        """
        Delete a document from the knowledge base.
        
        Args:
            document_id: Document ID to delete
        
        Returns:
            True if deleted, False if not found
        """
        if document_id not in self._documents:
            return False
        
        # Delete from ChromaDB
        try:
            # Get all chunk IDs for this document
            results = self.collection.get(
                where={"document_id": document_id}
            )
            if results and results.get("ids"):
                self.collection.delete(ids=results["ids"])
        except Exception:
            pass
        
        # Remove from local storage
        del self._documents[document_id]
        
        return True


# Global RAG service instance
_rag_service: Optional[RAGService] = None


def get_rag_service() -> RAGService:
    """Get or create RAG service instance."""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service
