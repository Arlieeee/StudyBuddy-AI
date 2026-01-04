"""Q&A router for RAG-based question answering."""
from fastapi import APIRouter, HTTPException
from typing import Optional, List

from ..models.schemas import QuestionRequest, AnswerResponse, SourceReference
from ..services.rag_service import get_rag_service

router = APIRouter(prefix="/qa", tags=["qa"])


@router.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    """
    Ask a question about the knowledge base.
    
    The system will search relevant documents and generate an answer.
    """
    rag_service = get_rag_service()
    
    try:
        result = await rag_service.answer_question(
            question=request.question,
            document_ids=request.document_ids,
        )
        
        return AnswerResponse(
            answer=result["answer"],
            sources=result["sources"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"问答处理失败: {str(e)}")


@router.post("/search")
async def search_documents(
    query: str,
    top_k: int = 5,
    document_ids: Optional[List[str]] = None,
):
    """
    Search for relevant document chunks.
    
    Returns matching text chunks without generating an answer.
    """
    rag_service = get_rag_service()
    
    try:
        results = await rag_service.search(
            query=query,
            top_k=top_k,
            document_ids=document_ids,
        )
        
        return {
            "query": query,
            "results": results,
            "total": len(results),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")
