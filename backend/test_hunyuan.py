#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
腾讯混元 API 测试脚本
用于测试腾讯混元 API 的连接和配置
"""
import os
import sys
from dotenv import load_dotenv

def test_hunyuan_api():
    """测试腾讯混元 API"""
    print("腾讯混元 API 诊断脚本")
    print("=" * 50)
    
    # 加载环境变量
    load_dotenv()
    
    # 检查环境变量
    secret_id = os.getenv("HUNYUAN_SECRET_ID")
    secret_key = os.getenv("HUNYUAN_SECRET_KEY")
    model_name = os.getenv("HUNYUAN_MODEL", "hunyuan-turbo")
    
    print(f"配置检查:")
    print(f"   Secret ID: {'已配置' if secret_id and secret_id != 'your_hunyuan_secret_id_here' else '未配置或使用默认值'}")
    print(f"   Secret Key: {'已配置' if secret_key and secret_key != 'your_hunyuan_secret_key_here' else '未配置或使用默认值'}")
    print(f"   模型名称: {model_name}")
    
    if not secret_id or secret_id == "your_hunyuan_secret_id_here":
        print("\nSecret ID 未正确配置！")
        print("请在 .env 文件中设置 HUNYUAN_SECRET_ID")
        return False
    
    if not secret_key or secret_key == "your_hunyuan_secret_key_here":
        print("\nSecret Key 未正确配置！")
        print("请在 .env 文件中设置 HUNYUAN_SECRET_KEY")
        print("您可以在腾讯云控制台获取: https://console.cloud.tencent.com/cam/capi")
        return False
    
    # 测试 API 连接
    try:
        print(f"\n测试 API 连接...")
        
        # 导入腾讯混元服务
        sys.path.append('.')
        from app.services.llm.hunyuan import HunyuanService
        
        # 创建服务实例
        service = HunyuanService(
            secret_id=secret_id,
            secret_key=secret_key,
            model_name=model_name
        )
        
        print(f"腾讯混元服务初始化成功: {service.get_provider_name()}")
        
        # 测试简单对话
        print(f"\n测试对话功能...")
        test_messages = [
            {"role": "user", "content": "你好，请简单介绍一下你自己。"}
        ]
        
        import asyncio
        async def test_chat():
            response = await service.chat_completion(test_messages)
            return response
        
        response = asyncio.run(test_chat())
        
        if "抱歉" not in response and "问题" not in response and "错误" not in response:
            print(f"✓ API 调用成功！")
            print(f"📝 响应内容: {response[:100]}...")
            return True
        else:
            print(f"❌ API 调用失败")
            print(f"📝 错误响应: {response}")
            return False
            
    except Exception as e:
        print(f"腾讯混元API调用失败: {str(e)}")
        
        # 常见错误的解决建议
        error_str = str(e).lower()
        if "secret" in error_str or "authentication" in error_str:
            print("\n解决建议:")
            print("   1. 检查 Secret ID 和 Secret Key 是否正确")
            print("   2. 确认密钥是否有效且未过期")
            print("   3. 访问 https://console.cloud.tencent.com/cam/capi 获取有效的密钥")
        elif "quota" in error_str or "limit" in error_str:
            print("\n解决建议:")
            print("   1. 检查腾讯云账户余额")
            print("   2. 确认混元大模型服务是否已开通")
            print("   3. 检查 API 调用配额")
        elif "network" in error_str or "connection" in error_str:
            print("\n解决建议:")
            print("   1. 检查网络连接")
            print("   2. 确认防火墙设置")
            print("   3. 尝试使用代理")
        
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
        print(f"   Hunyuan Secret ID: {'已配置' if settings.HUNYUAN_SECRET_ID != 'your_hunyuan_secret_id_here' else '未配置'}")
        print(f"   Hunyuan Secret Key: {'已配置' if settings.HUNYUAN_SECRET_KEY != 'your_hunyuan_secret_key_here' else '未配置'}")
        print(f"   Hunyuan Model: {settings.HUNYUAN_MODEL}")
        
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
        if "抱歉" not in response and "问题" not in response and "错误" not in response:
            print(f"✓ 应用集成测试成功！")
            print(f"📝 响应内容: {response[:100]}...")
            return True
        else:
            print(f"⚠️  应用集成测试失败")
            print(f"📝 错误响应: {response}")
            return False
            
    except Exception as e:
        print(f"应用集成测试失败: {str(e)}")
        return False

if __name__ == "__main__":
    print("开始腾讯混元 API 诊断...")
    
    # 测试 API
    api_ok = test_hunyuan_api()
    
    # 测试应用集成
    app_ok = test_app_integration()
    
    print(f"\n诊断结果:")
    print(f"   API 连接: {'正常' if api_ok else '异常'}")
    print(f"   应用集成: {'正常' if app_ok else '异常'}")
    
    if api_ok and app_ok:
        print(f"\n腾讯混元 API 配置正常，可以正常使用！")
    else:
        print(f"\n请根据上述建议修复问题后重试。")
        print(f"\n注意事项：")
        print(f"   1. 确保已在腾讯云开通混元大模型服务")
        print(f"   2. 检查账户余额是否充足")
        print(f"   3. 确认 Secret ID 和 Secret Key 配置正确")
