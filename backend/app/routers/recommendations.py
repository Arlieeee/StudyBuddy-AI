"""API routes for recommendation endpoints."""
from typing import List, Optional
from fastapi import APIRouter
from pydantic import BaseModel

from ..services.recommendation_service import get_recommendation_service, VisualizationTopic


router = APIRouter(prefix="/recommendations", tags=["recommendations"])


class VisualizationRecommendationRequest(BaseModel):
    """Request for visualization topic recommendations."""
    document_ids: Optional[List[str]] = None
    conversation_history: Optional[List[dict]] = None


class VisualizationRecommendationResponse(BaseModel):
    """Response containing visualization recommendations."""
    topics: List[VisualizationTopic]



class ChatRecommendationRequest(BaseModel):
    """Request for chat topic recommendations."""
    document_ids: Optional[List[str]] = None
    conversation_history: Optional[List[dict]] = None


class ChatRecommendationResponse(BaseModel):
    """Response containing chat recommendations."""
    topics: List[VisualizationTopic]


@router.post("/visualization", response_model=VisualizationRecommendationResponse)
async def get_visualization_recommendations(
    request: VisualizationRecommendationRequest
):
    """
    Get smart visualization topic recommendations.
    
    Analyzes uploaded documents and conversation history to suggest
    relevant topics for diagram/visualization generation.
    """
    service = get_recommendation_service()
    topics = await service.get_visualization_topics(
        document_ids=request.document_ids,
        conversation_history=request.conversation_history,
    )
    return VisualizationRecommendationResponse(topics=topics)


@router.post("/chat", response_model=ChatRecommendationResponse)
async def get_chat_recommendations(
    request: ChatRecommendationRequest
):
    """
    Get smart chat topic recommendations.
    
    Analyzes uploaded documents and conversation history to suggest
    relevant questions or actions for the chat interface.
    """
    service = get_recommendation_service()
    topics = await service.get_chat_topics(
        document_ids=request.document_ids,
        conversation_history=request.conversation_history,
    )
    return ChatRecommendationResponse(topics=topics)
