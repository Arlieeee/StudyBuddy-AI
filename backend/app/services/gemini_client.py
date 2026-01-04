"""Gemini API client wrapper using google-genai SDK."""
from google import genai
from google.genai import types
from typing import Optional
import base64

from ..config import get_settings


class GeminiClient:
    """Client for interacting with Google Gemini API."""
    
    def __init__(self):
        """Initialize the Gemini client."""
        self.settings = get_settings()
        self.client = genai.Client(api_key=self.settings.GOOGLE_API_KEY)
    
    async def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
    ) -> str:
        """
        Generate text response using Gemini 3 Flash.
        
        Args:
            prompt: The user prompt
            system_instruction: Optional system instruction
        
        Returns:
            Generated text response
        """
        config = None
        if system_instruction:
            config = types.GenerateContentConfig(
                system_instruction=system_instruction
            )
        
        response = self.client.models.generate_content(
            model=self.settings.GEMINI_FLASH_MODEL,
            contents=prompt,
            config=config,
        )
        
        return response.text
    
    async def generate_with_context(
        self,
        question: str,
        context: str,
        system_instruction: Optional[str] = None,
    ) -> str:
        """
        Generate answer using RAG context.
        
        Args:
            question: User's question
            context: Retrieved context from knowledge base
            system_instruction: Optional system instruction
        
        Returns:
            Generated answer
        """
        default_instruction = """你是一个智能学习助手，基于提供的知识库内容回答用户问题。

规则：
1. 只使用提供的上下文信息回答问题
2. 如果上下文中没有相关信息，明确说明
3. 回答要准确、简洁、有条理
4. 适当引用来源内容
5. 使用中文回答"""
        
        prompt = f"""# 知识库内容
{context}

# 用户问题
{question}

请基于以上知识库内容回答用户问题。如果知识库中没有相关信息，请明确说明。"""
        
        return await self.generate_text(
            prompt=prompt,
            system_instruction=system_instruction or default_instruction,
        )
    
    async def generate_image(
        self,
        prompt: str,
        aspect_ratio: str = "16:9",
    ) -> Optional[bytes]:
        """
        Generate image using Gemini image models.
        
        Args:
            prompt: Image generation prompt
            aspect_ratio: Aspect ratio (unused for now)
        
        Returns:
            Image bytes or None if failed
        
        Note:
            使用gemini-2.5-flash-image模型进行图像生成
            根据官方文档的最简示例
        """
        try:
            # 官方文档中的多轮图片修改示例（使用了google search工具）
            # response = self.client.models.
            # generate_content(
            #     model="gemini-3-pro-image-preview",
            #     config=types.GenerateContentConfig(
            #           response_modalities=['TEXT','IMAGE'],
            #           tools=[{"google_search":{}}]
            #     )
            # )
            # message = ""
            # response = chat.sent_message(message)
            # for part in response.parts:
                # if part.next is not None:
                #     print(part.text)
                # elif image:= part.as_image():
                #     image.save("photores.png")
            
            # message = "Update this visualization result to be in english. Do not change any other elements of the image."
            # aspect_ratio = "9:16" # "1:1","2:3","3:2","3:4","4:3","4:5","5:4","9:16","16:9","21:9"
            # resolution = "1K" # "1K", "2K", "4K"

            # response = chat.send_message(message,
            #     config=types.GenerateContentConfig(
            #         image_config=types.ImageConfig(
            #             aspect_ratio=aspect_ratio,
            #             image_size=resolution
            #         ),
            #     ))

            # for part in response.parts:
            #     if part.text is not None:
            #         print(part.text)
            #     elif image:= part.as_image():
            #         image.save("photosynthesis_spanish.png")

            # 使用 gemini-3-pro-image-preview 模型，需要配置 response_modalities
            # 根据官方文档，必须指定 response_modalities=['TEXT', 'IMAGE'] 才能返回图像
            config = types.GenerateContentConfig(
                response_modalities=['TEXT', 'IMAGE']
            )
            
            response = self.client.models.generate_content(
                model="gemini-3-pro-image-preview",
                contents=[prompt],
                config=config,
            )
            
            print(f"[Image Gen] Response type: {type(response)}")
            
            # 处理response
            if hasattr(response, 'candidates') and response.candidates:
                for part in response.candidates[0].content.parts:
                    # 处理思考过程（Thinking模式）
                    if hasattr(part, 'thought') and part.thought:
                        print(f"[Image Gen] Model thinking...")
                    # 处理文本部分
                    elif hasattr(part, 'text') and part.text:
                        print(f"[Image Gen] Model text: {part.text[:200] if len(part.text) > 200 else part.text}")
                    # 处理图像部分
                    elif hasattr(part, 'inline_data') and part.inline_data:
                        inline_data = part.inline_data
                        print(f"[Image Gen] inline_data type: {type(inline_data.data)}")
                        print(f"[Image Gen] inline_data.data length: {len(inline_data.data) if inline_data.data else 0}")
                        print(f"[Image Gen] mime_type: {getattr(inline_data, 'mime_type', 'unknown')}")
                        
                        # 返回图像数据
                        if isinstance(inline_data.data, bytes):
                            print(f"[Image Gen] Data is bytes, returning directly")
                            return inline_data.data
                        elif isinstance(inline_data.data, str):
                            import base64
                            print(f"[Image Gen] Data is str, decoding from base64")
                            image_data = base64.b64decode(inline_data.data)
                            print(f"[Image Gen] Decoded bytes length: {len(image_data)}")
                            return image_data
                        else:
                            print(f"[Image Gen] Unknown data type: {type(inline_data.data)}")
            
            if hasattr(response, 'text') and response.text:
                print(f"[Image Gen] Only text response: {response.text[:200]}")
            
            print(f"[Image Gen] No image in response")
            return None
            
        except Exception as e:
            print(f"[Image Gen] Error: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
    
    async def analyze_document(
        self,
        text_content: str,
        task: str = "summarize",
    ) -> str:
        """
        Analyze document content.
        
        Args:
            text_content: Document text
            task: Analysis task (summarize, extract_key_points, etc.)
        
        Returns:
            Analysis result
        """
        task_prompts = {
            "summarize": "请对以下内容进行简洁的摘要总结：",
            "extract_key_points": "请提取以下内容的关键知识点：",
            "generate_questions": "请基于以下内容生成可能的考试问题：",
        }
        
        prompt = f"""{task_prompts.get(task, task_prompts["summarize"])}

{text_content}"""
        
        return await self.generate_text(prompt)


# Global client instance
_client: Optional[GeminiClient] = None


def get_gemini_client() -> GeminiClient:
    """Get or create the Gemini client instance."""
    global _client
    if _client is None:
        _client = GeminiClient()
    return _client
