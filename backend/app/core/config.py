from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # LLM配置
    LLM_PROVIDER: str = "mock"  # mock | new_gradio | deepseek_gradio | gemini | hunyuan

    # 新Gradio API配置
    NEW_GRADIO_API_URL: str = "https://haiyangpengai-careyou.ms.show/"

    # DeepSeek API配置
    DEEPSEEK_API_URL: str = "Mengnankk/deepseek-ai-DeepSeek-V3.1-test"

    # Gemini API配置
    GEMINI_API_KEY: str = "your_gemini_api_key_here"
    GEMINI_MODEL: str = "gemini-2.0-flash-exp"  # 模型名称

        # 腾讯混元API配置
    HUNYUAN_SECRET_ID: str = "your_hunyuan_secret_id_here"
    HUNYUAN_SECRET_KEY: str = "your_hunyuan_secret_key_here"
    HUNYUAN_MODEL: str = "hunyuan-turbo"  # hunyuan-turbo | hunyuan-lite | hunyuan-pro

    # gRPC 配置（用于 Gemini API）
    GRPC_VERBOSITY: str = "ERROR"
    GRPC_TRACE: str = ""

    # 数据库配置
    DATABASE_URL: str = "sqlite+aiosqlite:///./ai_companion.db"

    # 应用配置
    APP_NAME: str = "AI灵魂伙伴"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # CORS配置
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173,http://localhost:5174,http://localhost:8080"

    # 会话配置
    SESSION_EXPIRE_SECONDS: int = 3600
    MAX_CONTEXT_MESSAGES: int = 10

    # Redis配置
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT认证配置
    SECRET_KEY: str = "your-secret-key-please-change-in-production-09af8sd7f9a8sdf7a9s8df7"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7天

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def allowed_origins_list(self) -> List[str]:
        """将CORS配置转为列表"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]


settings = Settings()
