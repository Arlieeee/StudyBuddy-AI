"""Image generation service using Gemini 3 Pro Image."""
import base64
from typing import Optional
from .gemini_client import get_gemini_client


class ImageGenerator:
    """Generate educational visualizations using Gemini 3 Pro Image."""
    
    def __init__(self):
        """Initialize image generator."""
        self.gemini = get_gemini_client()
    
    async def generate_knowledge_visualization(
        self,
        topic: str,
        knowledge_context: Optional[str] = None,
        conversation_history: Optional[str] = None,
        style: str = "educational",
        aspect_ratio: str = "16:9",
    ) -> Optional[str]:
        """
        Generate a knowledge visualization image using two-step strategy.
        
        Step 1: Use text model to plan the visualization content
        Step 2: Use image model to generate the visualization with planned content
        
        Args:
            topic: The topic to visualize
            knowledge_context: Additional context from RAG knowledge base
            conversation_history: Previous conversation context for continuity
            style: Visualization style
            aspect_ratio: Image aspect ratio
        
        Returns:
            Base64 encoded image string
        """
        # Style descriptions
        style_descriptions = {
            "educational": "清晰的教育图解风格，使用简洁的图标、方框和箭头展示概念关系",
            "diagram": "专业的流程图或架构图风格，使用统一的方框和连接线",
            "mindmap": "思维导图风格，从中心向外层层发散",
            "infographic": "信息图表风格，使用图表、统计数据和可视化元素",
        }
        style_desc = style_descriptions.get(style, style_descriptions["educational"])
        
        # ========== Step 1: 使用文本模型规划图像内容 ==========
        # 按照官方文档建议：先生成文本内容，再请求包含该文本的图像
        planning_prompt = f"""你是一个专业的学习辅助专家。请为以下主题设计一个知识可视化图解的详细内容规划。

主题：{topic}

"""
        if knowledge_context:
            planning_prompt += f"""相关知识背景（来自学习资料）：
{knowledge_context[:2000]}

"""
        if conversation_history:
            planning_prompt += f"""之前的对话复习内容：
{conversation_history[:1000]}

"""
        planning_prompt += f"""请输出用于图像生成的详细规划，包括：

1. 图解标题（简洁明了，最多10个汉字）
2. 核心概念节点（3-6个关键概念，每个概念用引号包围）
3. 概念之间的关系描述（用箭头符号如 → 表示方向）
4. 每个概念的简短说明（每个最多15个汉字）
5. 建议的布局方式（如：中心放射、流程线性、层级结构等）

要求：
- 所有文字使用简体中文
- 确保术语准确、专业
- 内容适合用于复习和记忆

请直接输出规划内容，不需要额外解释。"""

        try:
            # 调用文本模型规划内容
            planned_content = await self.gemini.generate_text(
                prompt=planning_prompt,
                system_instruction="你是一个专业的教育可视化内容规划师，擅长将复杂知识结构化为清晰的图解方案。"
            )
            print(f"[Image Generator] Planned content: {planned_content[:300]}...")
        except Exception as e:
            print(f"[Image Generator] Planning failed: {e}")
            planned_content = f"主题：{topic}\n核心概念：请根据主题生成"
        
        # ========== Step 2: 使用图像模型生成可视化 ==========
        # 构建图像生成提示，包含预规划的内容
        image_prompt = f"""请生成一张用于学习复习的知识可视化图解。

=== 图解规范 ===
风格：{style_desc}
用途：学习笔记、知识复习、思维导图

=== 内容规划 ===
{planned_content}

=== 设计要求 ===
1. 【文字清晰】所有中文文字必须清晰可读，字体规整，不能有乱码或模糊
2. 【布局清晰】使用清晰的视觉层次和对比色彩
3. 【专业美观】采用现代简约的设计风格，配色和谐
4. 【便于记忆】突出重点概念，使用颜色区分不同层级
5. 【适合复习】内容组织有助于知识的回顾和巩固

请确保生成的图像中所有文字都是正确的简体中文，无错别字。"""

        image_bytes = await self.gemini.generate_image(
            prompt=image_prompt,
            aspect_ratio=aspect_ratio,
        )
        
        if image_bytes:
            return base64.b64encode(image_bytes).decode("utf-8")
        
        return None
    
    async def generate_study_notes_image(
        self,
        notes_content: str,
        title: str = "学习笔记",
        aspect_ratio: str = "9:16",
    ) -> Optional[str]:
        """
        Generate a visual study notes image.
        
        Args:
            notes_content: The notes content to visualize
            title: Title of the notes
            aspect_ratio: Image aspect ratio
        
        Returns:
            Base64 encoded image string
        """
        prompt = f"""创建一个精美的学习笔记可视化图像。

标题：{title}

内容要点：
{notes_content[:1500]}

设计要求：
1. 采用卡片式布局
2. 使用渐变色背景
3. 重点内容使用高亮
4. 添加适当的图标装饰
5. 保持整体美观和可读性
6. 适合手机屏幕查看"""
        
        image_bytes = await self.gemini.generate_image(
            prompt=prompt,
            aspect_ratio=aspect_ratio,
        )
        
        if image_bytes:
            return base64.b64encode(image_bytes).decode("utf-8")
        
        return None
    
    async def generate_concept_map(
        self,
        concepts: list,
        central_topic: str,
        aspect_ratio: str = "16:9",
    ) -> Optional[str]:
        """
        Generate a concept map image.
        
        Args:
            concepts: List of related concepts
            central_topic: The central topic
            aspect_ratio: Image aspect ratio
        
        Returns:
            Base64 encoded image string
        """
        concepts_text = "\n".join([f"- {c}" for c in concepts[:10]])
        
        prompt = f"""创建一个概念关系图。

中心主题：{central_topic}

相关概念：
{concepts_text}

设计要求：
1. 中心主题放在图像中央
2. 相关概念围绕中心分布
3. 用连接线表示概念之间的关系
4. 使用不同颜色区分概念类别
5. 添加简短的关系说明
6. 整体布局清晰美观"""
        
        image_bytes = await self.gemini.generate_image(
            prompt=prompt,
            aspect_ratio=aspect_ratio,
        )
        
        if image_bytes:
            return base64.b64encode(image_bytes).decode("utf-8")
        
        return None


# Global image generator instance
_image_generator: Optional[ImageGenerator] = None


def get_image_generator() -> ImageGenerator:
    """Get or create image generator instance."""
    global _image_generator
    if _image_generator is None:
        _image_generator = ImageGenerator()
    return _image_generator
