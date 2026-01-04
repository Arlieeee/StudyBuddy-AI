"""Image generation router."""
from fastapi import APIRouter, HTTPException
from typing import Optional, List

from ..models.schemas import ImageGenerateRequest, ImageResponse
from ..services.image_generator import get_image_generator
from ..services.rag_service import get_rag_service

router = APIRouter(prefix="/generate", tags=["generate"])


@router.post("/visualization", response_model=ImageResponse)
async def generate_visualization(request: ImageGenerateRequest):
    """
    Generate a knowledge visualization image.
    
    Uses two-step strategy:
    1. Plan content using text model with RAG context
    2. Generate image using image model
    """
    generator = get_image_generator()
    
    # Get context from knowledge base if provided
    context = request.knowledge_context
    conversation = request.conversation_history
    
    try:
        image_base64 = await generator.generate_knowledge_visualization(
            topic=request.prompt,
            knowledge_context=context,
            conversation_history=conversation,
            style=request.style,
            aspect_ratio=request.aspect_ratio,
        )
        
        if not image_base64:
            raise HTTPException(status_code=500, detail="图像生成失败")
        
        return ImageResponse(
            image_base64=image_base64,
            description=f"关于「{request.prompt}」的知识可视化图解",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"图像生成失败: {str(e)}")


@router.post("/notes", response_model=ImageResponse)
async def generate_notes_image(
    title: str,
    content: str,
    aspect_ratio: str = "9:16",
):
    """
    Generate a visual study notes image.
    
    Creates a beautiful notes card for easy review.
    """
    generator = get_image_generator()
    
    try:
        image_base64 = await generator.generate_study_notes_image(
            notes_content=content,
            title=title,
            aspect_ratio=aspect_ratio,
        )
        
        if not image_base64:
            raise HTTPException(status_code=500, detail="笔记图像生成失败")
        
        return ImageResponse(
            image_base64=image_base64,
            description=f"学习笔记：{title}",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"笔记图像生成失败: {str(e)}")


@router.post("/concept-map", response_model=ImageResponse)
async def generate_concept_map(
    central_topic: str,
    concepts: List[str],
    aspect_ratio: str = "16:9",
):
    """
    Generate a concept map image.
    
    Creates a visual representation of concept relationships.
    """
    generator = get_image_generator()
    
    try:
        image_base64 = await generator.generate_concept_map(
            concepts=concepts,
            central_topic=central_topic,
            aspect_ratio=aspect_ratio,
        )
        
        if not image_base64:
            raise HTTPException(status_code=500, detail="概念图生成失败")
        
        return ImageResponse(
            image_base64=image_base64,
            description=f"概念图：{central_topic}",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"概念图生成失败: {str(e)}")


@router.post("/from-knowledge")
async def generate_from_knowledge(
    topic: str,
    style: str = "educational",
    aspect_ratio: str = "16:9",
):
    """
    Generate visualization based on knowledge base content.
    
    Searches the knowledge base for related content and generates an image.
    """
    rag_service = get_rag_service()
    generator = get_image_generator()
    
    try:
        # Search for related content
        results = await rag_service.search(query=topic, top_k=3)
        
        if not results:
            context = None
        else:
            context = "\n\n".join([r["text"] for r in results])
        
        image_base64 = await generator.generate_knowledge_visualization(
            topic=topic,
            knowledge_context=context,
            style=style,
            aspect_ratio=aspect_ratio,
        )
        
        if not image_base64:
            raise HTTPException(status_code=500, detail="图像生成失败")
        
        return ImageResponse(
            image_base64=image_base64,
            description=f"基于知识库的「{topic}」可视化",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"图像生成失败: {str(e)}")
