#!/usr/bin/env python3
"""
Gemini API 诊断脚本
用于测试 Gemini API 的连接和配置
"""
import os
import sys
from dotenv import load_dotenv
import google.generativeai as genai

def test_gemini_api():
    """测试 Gemini API"""
    print("Gemini API 诊断脚本")
    print("=" * 50)
    
    # 加载环境变量
    load_dotenv()
    
    # 检查环境变量
    api_key = os.getenv("GEMINI_API_KEY")
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
    
    print(f"配置检查:")
    print(f"   API Key: {'已配置' if api_key and api_key != 'your_gemini_api_key_here' else '未配置或使用默认值'}")
    print(f"   模型名称: {model_name}")
    
    if not api_key or api_key == "your_gemini_api_key_here":
        print("\nAPI Key 未正确配置！")
        print("请在 .env 文件中设置 GEMINI_API_KEY")
        return False
    
    # 测试 API 连接
    try:
        print(f"\n测试 API 连接...")
        genai.configure(api_key=api_key)
        
        # 创建模型实例
        model = genai.GenerativeModel(model_name)
        print(f"模型初始化成功: {model_name}")
        
        # 测试简单对话
        print(f"\n测试对话功能...")
        test_prompt = "你好，请简单介绍一下你自己。"
        
        response = model.generate_content(
            test_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=100,
                top_p=0.95,
                top_k=40,
            ),
            safety_settings={
                'HATE': 'BLOCK_NONE',
                'HARASSMENT': 'BLOCK_NONE', 
                'SEXUAL': 'BLOCK_NONE',
                'DANGEROUS': 'BLOCK_NONE'
            }
        )
        
        if response.text:
            print(f"API 调用成功！")
            print(f"响应内容: {response.text[:100]}...")
            return True
        else:
            print(f"API 调用成功但没有返回内容")
            print(f"原始响应: {response}")
            return False
            
    except Exception as e:
        print(f"API 调用失败: {str(e)}")
        print(f"错误类型: {type(e).__name__}")
        
        # 常见错误的解决建议
        error_str = str(e).lower()
        if "api key" in error_str or "authentication" in error_str:
            print("\n解决建议:")
            print("   1. 检查 API Key 是否正确")
            print("   2. 确认 API Key 是否有效且未过期")
            print("   3. 访问 https://ai.google.dev/ 获取有效的 API Key")
        elif "quota" in error_str or "limit" in error_str:
            print("\n解决建议:")
            print("   1. 检查 API 配额是否用完")
            print("   2. 等待配额重置或升级账户")
        elif "network" in error_str or "connection" in error_str:
            print("\n解决建议:")
            print("   1. 检查网络连接")
            print("   2. 确认防火墙设置")
            print("   3. 尝试使用代理")
        elif "503" in error_str:
            print("\n解决建议:")
            print("   1. Gemini API 服务暂时不可用")
            print("   2. 稍后重试")
            print("   3. 检查 Google API 服务状态")
        
        return False

def test_app_integration():
    """测试应用集成"""
    print(f"\n测试应用集成...")
    
    try:
        # 导入应用模块
        sys.path.append('.')
        from app.services.llm.factory import LLMServiceFactory
        from app.core.config import settings
        
        print(f"应用配置:")
        print(f"   LLM Provider: {settings.LLM_PROVIDER}")
        print(f"   Gemini API Key: {'已配置' if settings.GEMINI_API_KEY != 'your_gemini_api_key_here' else '未配置'}")
        print(f"   Gemini Model: {settings.GEMINI_MODEL}")
        
        # 创建服务实例
        service = LLMServiceFactory.create_service()
        print(f"LLM 服务创建成功: {service.get_provider_name()}")
        
        # 测试对话
        import asyncio
        async def test_chat():
            messages = [
                {"role": "user", "content": "你好，请简单介绍一下你自己。"}
            ]
            response = await service.chat_completion(messages)
            return response
        
        response = asyncio.run(test_chat())
        if "抱歉" not in response and "问题" not in response:
            print(f"应用集成测试成功！")
            print(f"响应内容: {response[:100]}...")
            return True
        else:
            print(f"应用集成测试失败")
            print(f"错误响应: {response}")
            return False
            
    except Exception as e:
        print(f"应用集成测试失败: {str(e)}")
        return False

if __name__ == "__main__":
    print("开始 Gemini API 诊断...")
    
    # 测试 API
    api_ok = test_gemini_api()
    
    # 测试应用集成
    app_ok = test_app_integration()
    
    print(f"\n诊断结果:")
    print(f"   API 连接: {'正常' if api_ok else '异常'}")
    print(f"   应用集成: {'正常' if app_ok else '异常'}")
    
    if api_ok and app_ok:
        print(f"\nGemini API 配置正常，可以正常使用！")
    else:
        print(f"\n请根据上述建议修复问题后重试。")
