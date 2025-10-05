"""
Gemini LLM服务实现
使用Google Generative AI API
"""
from typing import List, Dict, Optional
import google.generativeai as genai
from app.services.llm.base import BaseLLMService


class GeminiService(BaseLLMService):
    """Gemini 2.5 Flash服务"""

    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash-exp"):
        """
        初始化Gemini服务

        Args:
            api_key: Google AI API密钥
            model_name: 模型名称，默认使用gemini-2.0-flash-exp
        """
        super().__init__(api_url=f"https://generativelanguage.googleapis.com")
        self.api_key = api_key
        self.model_name = model_name
        self.model = None
        self._initialize_client()

    def _initialize_client(self):
        """初始化Gemini客户端"""
        try:
            if not self.api_key or self.api_key == "your_gemini_api_key_here":
                print("⚠️  Gemini API Key未配置，请在.env文件中设置GEMINI_API_KEY")
                return

            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
            print(f"✓ Gemini客户端初始化成功 (模型: {self.model_name})")
        except Exception as e:
            print(f"✗ Gemini客户端初始化失败: {e}")
            self.model = None

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> str:
        """
        调用Gemini完成对话

        Args:
            messages: 消息历史 [{"role": "user/assistant/system", "content": "..."}]
            temperature: 温度参数 (0.0-1.0)
            max_tokens: 最大生成token数
            **kwargs: 其他参数

        Returns:
            模型回复内容
        """
        if not self.model:
            return "抱歉，Gemini服务暂时不可用。请检查API Key配置。"

        try:
            # 转换消息格式为Gemini格式
            gemini_messages = self._convert_messages(messages)

            # 配置生成参数
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                top_p=0.95,
                top_k=40,
            )

            # 调用Gemini API
            response = self.model.generate_content(
                gemini_messages,
                generation_config=generation_config,
                safety_settings={
                    'HATE': 'BLOCK_NONE',
                    'HARASSMENT': 'BLOCK_NONE',
                    'SEXUAL': 'BLOCK_NONE',
                    'DANGEROUS': 'BLOCK_NONE'
                }
            )

            # 提取回复文本
            if response.text:
                return response.text
            else:
                return "抱歉，我无法生成回复。"

        except Exception as e:
            print(f"Gemini API调用失败: {e}")
            return f"抱歉，调用Gemini时遇到问题: {str(e)}"

    def _convert_messages(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        将消息格式转换为Gemini API格式

        Gemini使用简单的对话格式，system消息会被合并到第一条user消息中
        """
        gemini_messages = []
        system_prompt = ""

        # 提取system消息
        for msg in messages:
            if msg["role"] == "system":
                system_prompt = msg["content"]
                break

        # 转换user和assistant消息
        for msg in messages:
            role = msg["role"]
            content = msg["content"]

            if role == "user":
                # 如果有system prompt且是第一条user消息，合并system prompt
                if system_prompt and not gemini_messages:
                    content = f"{system_prompt}\n\n{content}"
                gemini_messages.append({
                    "role": "user",
                    "parts": [content]
                })
            elif role == "assistant":
                gemini_messages.append({
                    "role": "model",  # Gemini使用"model"而不是"assistant"
                    "parts": [content]
                })

        return gemini_messages

    def get_provider_name(self) -> str:
        """返回提供商名称"""
        return f"Google Gemini ({self.model_name})"
