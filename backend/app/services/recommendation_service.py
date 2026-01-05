"""Recommendation service for generating visualization topic suggestions."""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from .rag_service import get_rag_service
from .gemini_client import get_gemini_client
from .keyword_extractor import get_keyword_extractor


class VisualizationTopic(BaseModel):
    """A recommended visualization topic."""
    type: str  # "overview", "concept", "chapter"
    title: str
    description: str
    prompt: str  # The actual prompt to use for image generation


class RecommendationService:
    """Service for generating smart recommendations based on RAG and conversation history."""
    
    async def get_visualization_topics(
        self,
        document_ids: Optional[List[str]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> List[VisualizationTopic]:
        """
        Generate visualization topic recommendations.
        
        Analyzes uploaded documents and conversation history to suggest
        relevant topics for diagram/visualization generation.
        
        Args:
            document_ids: Optional list of document IDs to analyze
            conversation_history: List of {"role": "user"|"assistant", "content": "..."}
        
        Returns:
            List of recommended visualization topics
        """
        rag = get_rag_service()
        gemini = get_gemini_client()
        keyword_extractor = get_keyword_extractor()
        
        # Get document summaries
        documents = rag.list_documents()
        if document_ids:
            documents = [d for d in documents if d["id"] in document_ids]
        
        if not documents:
            # No documents, return default suggestions
            return [
                VisualizationTopic(
                    type="overview",
                    title="请先上传学习资料",
                    description="上传 PDF 或文档后，我会根据内容推荐可视化主题",
                    prompt=""
                )
            ]
        
        # Get sample content from documents for analysis
        doc_samples = []
        all_content_for_keywords = []  # Collect content for TF-IDF analysis
        
        for doc in documents[:3]:  # Limit to 3 documents
            results = await rag.search(
                query="主要内容概述",
                top_k=2,
                document_ids=[doc["id"]]
            )
            if results:
                content = "\n".join([r["text"][:500] for r in results])
                doc_samples.append({
                    "filename": doc["filename"],
                    "content": content
                })
                all_content_for_keywords.append(content)
        
        # === NEW: TF-IDF Keyword Extraction ===
        extracted_keywords = []
        if all_content_for_keywords:
            try:
                extracted_keywords = keyword_extractor.get_trending_topics(
                    all_content_for_keywords, 
                    top_n=15
                )
                print(f"[Recommendation] Extracted TF-IDF keywords: {extracted_keywords}")
            except Exception as e:
                print(f"[Recommendation] Keyword extraction failed: {e}")
        
        # Analyze conversation for frequently mentioned concepts
        frequent_concepts = ""
        if conversation_history:
            # Extract user messages
            user_messages = [
                m["content"] for m in conversation_history 
                if m.get("role") == "user" and m.get("content")
            ][-10:]  # Last 10 messages
            if user_messages:
                frequent_concepts = "\n".join(user_messages)
        
        # Build prompt for Gemini to generate recommendations
        keywords_section = ""
        if extracted_keywords:
            keywords_section = f"\n## 🔑 TF-IDF 提取的高频关键词\n{', '.join(extracted_keywords[:15])}\n"
        
        prompt = f"""基于以下学习资料和用户对话历史，生成5个适合制作可视化图解的主题推荐。

## 学习资料内容摘要
{chr(10).join([f"### {s['filename']}{chr(10)}{s['content']}" for s in doc_samples]) if doc_samples else "暂无资料摘要"}
{keywords_section}
## 用户近期提问/关注概念
{frequent_concepts if frequent_concepts else "暂无对话历史"}

## 要求
请基于上述**关键词**和资料内容，生成5个可视化主题推荐，每个主题包含：
1. type: 类型，只能是 "overview"(全局概览)、"concept"(具体概念)、"chapter"(章节总结) 之一
2. title: 简短标题（10字以内），必须包含关键词中的核心概念
3. description: 描述（20字以内）
4. prompt: 用于生成图解的完整提示词

返回JSON数组格式，例如：
[
  {{"type": "overview", "title": "全局知识框架", "description": "整体知识结构概览", "prompt": "生成关于[主题]的全局知识结构思维导图"}},
  {{"type": "concept", "title": "核心算法对比", "description": "比较不同算法特点", "prompt": "生成[算法A]与[算法B]的对比流程图"}}
]

只返回JSON数组，不要其他内容。"""

        try:
            response = await gemini.generate_text(
                prompt=prompt,
                system_instruction="你是一个学习助手，负责分析学习资料并推荐适合可视化的知识点。只返回有效的JSON数组。"
            )
            
            # Parse response
            import json
            # Clean response - remove markdown code blocks if present
            text = response.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1] if "\n" in text else text
            if text.endswith("```"):
                text = text.rsplit("```", 1)[0]
            if text.startswith("json"):
                text = text[4:].strip()
            
            topics_data = json.loads(text)
            
            topics = []
            for item in topics_data[:5]:  # Limit to 5
                topics.append(VisualizationTopic(
                    type=item.get("type", "concept"),
                    title=item.get("title", "未命名主题"),
                    description=item.get("description", ""),
                    prompt=item.get("prompt", item.get("title", ""))
                ))
            
            return topics
            
        except Exception as e:
            print(f"Error generating recommendations: {e}")
            # Return fallback recommendations based on document names
            topics = []
            for doc in documents[:3]:
                topics.append(VisualizationTopic(
                    type="overview",
                    title=f"{doc['filename'][:15]}概览",
                    description="整体知识结构",
                    prompt=f"生成关于{doc['filename']}的知识结构思维导图"
                ))
            if not topics:
                topics.append(VisualizationTopic(
                    type="overview",
                    title="知识框架总览",
                    description="所有学习资料的整体结构",
                    prompt="生成学习资料的整体知识框架思维导图"
                ))
            return topics



    async def get_chat_topics(
        self,
        document_ids: Optional[List[str]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> List[VisualizationTopic]:
        """
        Generate chat topic recommendations.
        
        Args:
            document_ids: Optional list of document IDs
            conversation_history: User conversation history
            
        Returns:
            List of recommended chat topics/questions
        """
        rag = get_rag_service()
        gemini = get_gemini_client()
        
        # Get document summaries
        documents = rag.list_documents()
        if document_ids:
            documents = [d for d in documents if d["id"] in document_ids]
            
        if not documents:
            return [
                VisualizationTopic(
                    type="summary",
                    title="请先上传文档",
                    description="上传文档后，我可以帮你总结内容或回答问题",
                    prompt=""
                )
            ]
            
        # Get sample content
        doc_samples = []
        for doc in documents[:3]:
            # Use specific samples or just first chunk
            doc_samples.append({
                "filename": doc["filename"],
                "content": f"Document: {doc['filename']}" # Minimal context needed for generic questions, but better if we have content
            })
            # Try to get some actual content if possible, reusing logic from visualization
            results = await rag.search(query="summary", top_k=1, document_ids=[doc["id"]])
            if results:
                 doc_samples[-1]["content"] += f"\nContent: {results[0]['text'][:800]}"

        # Analyze history
        recent_context = ""
        if conversation_history:
            user_msgs = [m["content"] for m in conversation_history if m.get("role") == "user"][-5:]
            if user_msgs:
                recent_context = "\n".join(user_msgs)

        prompt = f"""基于以下文档内容和用户对话，生成4个值得提问的问题或指令推荐。
        
## 文档摘要
{chr(10).join([f"### {s['filename']}{chr(10)}{s['content']}" for s in doc_samples])}

## 用户近期对话
{recent_context if recent_context else "无"}

## 要求
生成4个推荐，覆盖以下类型：
1. summary (文档摘要)
2. concept (解释核心概念)
3. qa (针对具体细节提问)
4. review (生成复习题)

返回JSON数组，格式如下：
[
  {{"type": "summary", "title": "总结文档内容", "description": "快速了解核心观点", "prompt": "这份文档的主要内容是什么？"}},
  {{"type": "concept", "title": "解释[某概念]", "description": "深入理解核心概念", "prompt": "请解释一下[某概念]的定义和原理"}},
  {{"type": "qa", "title": "关于[某细节]", "description": "探索文档具体细节", "prompt": "关于[某技术]有什么关键点？"}},
  {{"type": "review", "title": "生成复习题", "description": "巩固知识点", "prompt": "基于文档内容生成3道复习思考题"}}
]
确保prompt是用户可以直接发送给AI的问题。只返回JSON数组。"""

        try:
            response = await gemini.generate_text(prompt=prompt)
            # Parse JSON logic similar to above
            import json
            text = response.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1] if "\n" in text else text
            if text.endswith("```"):
                text = text.rsplit("```", 1)[0]
            if text.startswith("json"):
                text = text[4:].strip()
                
            topics_data = json.loads(text)
            topics = []
            for item in topics_data[:4]:
                topics.append(VisualizationTopic(
                    type=item.get("type", "qa"),
                    title=item.get("title", "推荐问题"),
                    description=item.get("description", ""),
                    prompt=item.get("prompt", "")
                ))
            return topics
        except Exception as e:
            print(f"Error chat recommendations: {e}")
            # Fallback
            return [
                VisualizationTopic(type="summary", title="总结全文", description="生成文档摘要", prompt="这份文档主要讲了什么？"),
                VisualizationTopic(type="review", title="生成考题", description="测试知识掌握", prompt="基于文档生成5个复习题"),
            ]


# Global service instance
_recommendation_service: Optional[RecommendationService] = None



def get_recommendation_service() -> RecommendationService:
    """Get or create recommendation service instance."""
    global _recommendation_service
    if _recommendation_service is None:
        _recommendation_service = RecommendationService()
    return _recommendation_service
