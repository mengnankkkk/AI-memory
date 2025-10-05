"""
LLM服务工厂
根据配置创建对应的LLM服务实例
"""
from app.services.llm.base import BaseLLMService
from app.services.llm.mock import MockLLMService
from app.services.llm.new_gradio import NewGradioService
from app.services.llm.new_gradio_http import NewGradioHTTPService
from app.services.llm.deepseek_gradio import DeepSeekGradioService
from app.services.llm.gemini import GeminiService
from app.services.llm.hunyuan import HunyuanService
from app.core.config import settings


class LLMServiceFactory:
    """LLM服务工厂类"""

    @staticmethod
    def create_service() -> BaseLLMService:
        """
        根据配置创建LLM服务

        支持的提供商:
        - mock: Mock服务(用于测试)
        - new_gradio: 新Gradio API (Gradio Client)
        - new_gradio_http: 新Gradio API (HTTP直接调用，推荐)
        - deepseek_gradio: DeepSeek Gradio API (Hugging Face)
        - gemini: Google Gemini 2.5 Flash API
        - hunyuan: 腾讯混元大模型 API
        """
        provider = settings.LLM_PROVIDER.lower()

        if provider == "mock":
            return MockLLMService()

        elif provider == "new_gradio":
            api_url = settings.NEW_GRADIO_API_URL
            return NewGradioService(api_url=api_url)

        elif provider == "new_gradio_http":
            api_url = settings.NEW_GRADIO_API_URL
            return NewGradioHTTPService(api_url=api_url)

        elif provider == "deepseek_gradio":
            api_url = settings.DEEPSEEK_API_URL
            return DeepSeekGradioService(api_url=api_url)

        elif provider == "gemini":
            api_key = settings.GEMINI_API_KEY
            model_name = settings.GEMINI_MODEL
            return GeminiService(api_key=api_key, model_name=model_name)

        elif provider == "hunyuan":
            secret_id = settings.HUNYUAN_SECRET_ID
            secret_key = settings.HUNYUAN_SECRET_KEY
            model_name = settings.HUNYUAN_MODEL
            return HunyuanService(secret_id=secret_id, secret_key=secret_key, model_name=model_name)

        else:
            print(f"⚠️  未知的LLM提供商: {provider}，使用Mock模式")
            return MockLLMService()


# 全局单例
llm_service = LLMServiceFactory.create_service()
