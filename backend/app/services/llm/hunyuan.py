"""
腾讯混元大模型服务实现
使用腾讯云 API
"""
import asyncio
import json
import hashlib
import hmac
import time
from typing import List, Dict, Optional
from datetime import datetime
import requests
from app.services.llm.base import BaseLLMService


class HunyuanService(BaseLLMService):
    """腾讯混元大模型服务"""

    def __init__(self, secret_id: str, secret_key: str, model_name: str = "hunyuan-turbo"):
        """
        初始化腾讯混元服务

        Args:
            secret_id: 腾讯云 Secret ID
            secret_key: 腾讯云 Secret Key  
            model_name: 模型名称，默认使用 hunyuan-turbo
        """
        super().__init__(api_url="https://hunyuan.tencentcloudapi.com")
        self.secret_id = secret_id
        self.secret_key = secret_key
        self.model_name = model_name
        self.service = "hunyuan"
        self.version = "2023-09-01"
        self.action = "ChatCompletions"
        self.region = "ap-beijing"
        self.endpoint = "https://hunyuan.tencentcloudapi.com"
        
        print(f"[OK] 腾讯混元服务初始化成功 (模型: {model_name})")

    def _sign(self, secret_key: bytes, msg: str) -> bytes:
        """计算签名"""
        return hmac.new(secret_key, msg.encode('utf-8'), hashlib.sha256).digest()

    def _get_authorization(self, payload: str, timestamp: int) -> str:
        """生成腾讯云 API 签名"""
        # 步骤 1：拼接规范请求串
        http_method = "POST"
        canonical_uri = "/"
        canonical_querystring = ""
        canonical_headers = f"content-type:application/json; charset=utf-8\nhost:hunyuan.tencentcloudapi.com\nx-tc-action:{self.action.lower()}\n"
        signed_headers = "content-type;host;x-tc-action"
        hashed_request_payload = hashlib.sha256(payload.encode('utf-8')).hexdigest()
        canonical_request = f"{http_method}\n{canonical_uri}\n{canonical_querystring}\n{canonical_headers}\n{signed_headers}\n{hashed_request_payload}"

        # 步骤 2：拼接待签名字符串
        algorithm = "TC3-HMAC-SHA256"
        date = datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d")
        credential_scope = f"{date}/{self.service}/tc3_request"
        hashed_canonical_request = hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()
        string_to_sign = f"{algorithm}\n{timestamp}\n{credential_scope}\n{hashed_canonical_request}"

        # 步骤 3：计算签名
        secret_date = self._sign(f"TC3{self.secret_key}".encode('utf-8'), date)
        secret_service = self._sign(secret_date, self.service)
        secret_signing = self._sign(secret_service, "tc3_request")
        signature = hmac.new(secret_signing, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()

        # 步骤 4：拼接 Authorization
        authorization = f"{algorithm} Credential={self.secret_id}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}"
        return authorization

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        stream: bool = False,
        **kwargs
    ) -> str:
        """
        调用腾讯混元完成对话

        Args:
            messages: 消息历史 [{"role": "user/assistant/system", "content": "..."}]
            temperature: 温度参数 (0.0-2.0)
            max_tokens: 最大生成token数
            stream: 是否使用流式输出
            **kwargs: 其他参数

        Returns:
            模型回复内容
        """
        try:
            # 转换消息格式为腾讯混元格式
            hunyuan_messages = self._convert_messages(messages)

            # 构建请求体
            payload = {
                "Model": self.model_name,
                "Messages": hunyuan_messages,
                "Temperature": temperature,
                "Stream": stream
            }

            # 如果指定了 max_tokens，需要注意腾讯云的参数名可能不同
            # 腾讯混元使用模型默认的输出长度限制

            payload_json = json.dumps(payload, separators=(',', ':'))
            
            # 生成时间戳
            timestamp = int(time.time())
            
            # 生成签名
            authorization = self._get_authorization(payload_json, timestamp)

            # 构建请求头
            headers = {
                "Authorization": authorization,
                "Content-Type": "application/json; charset=utf-8",
                "Host": "hunyuan.tencentcloudapi.com",
                "X-TC-Action": self.action,
                "X-TC-Timestamp": str(timestamp),
                "X-TC-Version": self.version,
                "X-TC-Region": self.region
            }

            # 发送请求（使用 asyncio.to_thread 避免阻塞事件循环）
            response = await asyncio.to_thread(
                requests.post,
                self.endpoint,
                headers=headers,
                data=payload_json,
                timeout=30
            )

            # 检查响应状态
            if response.status_code != 200:
                print(f"腾讯混元API请求失败: HTTP {response.status_code}")
                print(f"响应内容: {response.text}")
                return f"抱歉，调用腾讯混元时遇到问题: HTTP {response.status_code}"

            # 解析响应
            result = response.json()

            # 检查是否有错误
            if "Response" in result and "Error" in result["Response"]:
                error = result["Response"]["Error"]
                print(f"腾讯混元API错误: {error['Code']} - {error['Message']}")
                return f"抱歉，腾讯混元返回错误: {error['Message']}"

            # 提取回复内容 - 支持两种响应格式
            choices = None
            if "Response" in result and "Choices" in result["Response"]:
                choices = result["Response"]["Choices"]
            elif "Choices" in result:
                choices = result["Choices"]

            if choices and len(choices) > 0:
                choice = choices[0]
                if "Message" in choice and "Content" in choice["Message"]:
                    return choice["Message"]["Content"]
                elif "Delta" in choice and "Content" in choice["Delta"]:
                    return choice["Delta"]["Content"]

            print(f"腾讯混元API响应格式异常: {result}")
            return "抱歉，腾讯混元返回了异常的响应格式。"

        except requests.exceptions.Timeout:
            print("腾讯混元API请求超时")
            return "抱歉，请求超时，请稍后重试。"
        except requests.exceptions.ConnectionError:
            print("腾讯混元API连接错误")
            return "抱歉，网络连接失败，请检查网络设置。"
        except Exception as e:
            print(f"腾讯混元API调用失败: {e}")
            return f"抱歉，调用腾讯混元时遇到问题: {str(e)}"

    def _convert_messages(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        将消息格式转换为腾讯混元API格式

        腾讯混元支持 system、user、assistant 角色
        """
        hunyuan_messages = []

        for msg in messages:
            role = msg["role"]
            content = msg["content"]

            if role in ["system", "user", "assistant"]:
                hunyuan_messages.append({
                    "Role": role,
                    "Content": content
                })

        return hunyuan_messages

    def get_provider_name(self) -> str:
        """返回提供商名称"""
        return f"腾讯混元 ({self.model_name})"
