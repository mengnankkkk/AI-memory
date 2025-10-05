"""
流式 LLM 服务
为不支持原生流式的 LLM 提供模拟流式输出
"""
import asyncio
import re
from typing import AsyncIterator, List, Dict
from app.services.llm.factory import llm_service

class StreamingLLMService:
    """流式 LLM 服务包装器"""
    
    def __init__(self):
        self.base_service = llm_service
    
    async def stream_chat_completion(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str = "",
        temperature: float = 0.8,
        max_tokens: int = 300,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        流式聊天完成
        
        Args:
            messages: 消息历史
            system_prompt: 系统提示词
            temperature: 温度参数
            max_tokens: 最大生成token数
            
        Yields:
            str: 流式文本块
        """
        try:
            # 如果有系统提示词，添加到消息开头
            if system_prompt:
                full_messages = [{"role": "system", "content": system_prompt}] + messages
            else:
                full_messages = messages
            
            # 调用基础 LLM 服务
            response = await self.base_service.chat_completion(
                messages=full_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            # 如果响应是错误消息，直接返回
            if not response or response.startswith("抱歉"):
                yield response or "我现在有点困惑，能再说一遍吗？😅"
                return
            
            # 将响应分解为自然的流式块
            async for chunk in self._simulate_streaming(response):
                yield chunk
                
        except Exception as e:
            yield f"抱歉，我遇到了一些技术问题：{str(e)} 😅"
    
    async def _simulate_streaming(self, text: str) -> AsyncIterator[str]:
        """
        模拟流式输出，提供自然的分块体验
        
        Args:
            text: 完整的回复文本
            
        Yields:
            str: 文本块
        """
        if not text:
            return
        
        # 清理文本
        text = text.strip()
        
        # 按句子分割（中文和英文）
        sentence_endings = r'[。！？\.!?]+'
        sentences = re.split(f'({sentence_endings})', text)
        
        current_sentence = ""
        
        for i in range(0, len(sentences), 2):
            if i < len(sentences):
                sentence_content = sentences[i].strip()
                
                # 获取标点符号
                punctuation = ""
                if i + 1 < len(sentences):
                    punctuation = sentences[i + 1]
                
                if sentence_content:
                    current_sentence = sentence_content + punctuation
                    
                    # 如果句子太长，按词分割
                    if len(current_sentence) > 50:
                        words = current_sentence.split()
                        current_chunk = ""
                        
                        for word in words:
                            current_chunk += word + " "
                            
                            # 每10-15个字符发送一次
                            if len(current_chunk) >= 15:
                                yield current_chunk.strip()
                                await asyncio.sleep(0.08)  # 控制流式速度
                                current_chunk = ""
                        
                        # 发送剩余部分
                        if current_chunk.strip():
                            yield current_chunk.strip()
                            await asyncio.sleep(0.2)  # 句子间停顿
                    else:
                        # 短句子直接发送
                        yield current_sentence
                        await asyncio.sleep(0.3)  # 句子间停顿
    
    async def get_response_preview(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str = "",
        max_length: int = 100
    ) -> str:
        """
        获取回复预览（非流式）
        
        Args:
            messages: 消息历史
            system_prompt: 系统提示词
            max_length: 最大预览长度
            
        Returns:
            预览文本
        """
        try:
            if system_prompt:
                full_messages = [{"role": "system", "content": system_prompt}] + messages
            else:
                full_messages = messages
            
            response = await self.base_service.chat_completion(
                messages=full_messages,
                temperature=0.7,
                max_tokens=max_length
            )
            
            return response[:max_length] if response else "..."
            
        except Exception:
            return "预览不可用"

# 全局流式 LLM 服务实例
streaming_llm_service = StreamingLLMService()
