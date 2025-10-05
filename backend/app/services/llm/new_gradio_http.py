"""
新Gradio API服务实现 (HTTP直接调用)
绕过 Gradio Client 的 sse_v3 协议问题
"""
import httpx
from typing import List, Dict
from app.services.llm.base import BaseLLMService


class NewGradioHTTPService(BaseLLMService):
    """新Gradio API服务 (HTTP版本)"""

    def __init__(self, api_url: str = "https://haiyangpengai-careyou.ms.show/"):
        super().__init__(api_url)
        # 确保URL以斜杠结尾
        if not self.api_url.endswith("/"):
            self.api_url += "/"
        print(f"✓ {self.get_provider_name()} 初始化成功")

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.6,
        max_tokens: int = 4096,
        **kwargs
    ) -> str:
        """
        调用新Gradio API完成对话 (通过HTTP直接调用)

        使用 /api/predict 端点
        """
        try:
            # 构建Gradio格式的历史记录
            history = self._build_history(messages)

            # 获取top_p参数
            top_p = kwargs.get("top_p", 0.95)

            # 调用 /api/predict 端点
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.api_url}api/predict",
                    json={
                        "fn_index": 0,  # 通常第一个函数是主要的对话接口
                        "data": [
                            history,
                            temperature,
                            top_p,
                            max_tokens
                        ]
                    }
                )

                if response.status_code != 200:
                    return f"抱歉，API调用失败: HTTP {response.status_code}"

                result = response.json()

                # 解析返回结果
                if "data" in result:
                    output = result["data"]
                    if output and len(output) > 0:
                        # output[0] 是更新后的 history
                        updated_history = output[0]
                        if updated_history and len(updated_history) > 0:
                            last_message = updated_history[-1]
                            if len(last_message) > 1 and last_message[1]:
                                return last_message[1]

                return "抱歉，没有收到回复"

        except Exception as e:
            print(f"{self.get_provider_name()} API调用失败: {e}")
            return f"抱歉，调用失败: {str(e)}"

    def get_provider_name(self) -> str:
        return "NewGradio HTTP API"
