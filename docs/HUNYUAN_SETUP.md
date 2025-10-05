# 腾讯混元大模型配置指南

## 概述

腾讯混元是腾讯自研的大语言模型，具备强大的中文理解和生成能力。本项目已集成腾讯混元大模型支持。

## 配置步骤

### 1. 获取腾讯云 API 密钥

1. 访问 [腾讯云控制台](https://console.cloud.tencent.com/)
2. 登录您的腾讯云账号
3. 进入 [访问管理-API密钥管理](https://console.cloud.tencent.com/cam/capi)
4. 点击"新建密钥"获取 Secret ID 和 Secret Key

### 2. 开通混元大模型服务

1. 访问 [腾讯混元大模型控制台](https://console.cloud.tencent.com/hunyuan)
2. 开通混元大模型服务
3. 确保账户余额充足

### 3. 配置环境变量

在 `.env` 文件中配置以下参数：

```bash
# LLM服务配置
LLM_PROVIDER=hunyuan

# 腾讯混元API配置
HUNYUAN_SECRET_ID=您的Secret_ID
HUNYUAN_SECRET_KEY=您的Secret_Key
HUNYUAN_MODEL=hunyuan-turbo
```

## 支持的模型

- `hunyuan-turbo`: 标准版本，平衡性能和成本
- `hunyuan-lite`: 轻量版本，更快的响应速度
- `hunyuan-pro`: 高级版本，更强的推理能力

## 测试配置

运行测试脚本验证配置：

```bash
python test_hunyuan.py
```

## 注意事项

1. **密钥安全**: 请妥善保管您的 Secret ID 和 Secret Key，不要提交到版本控制系统
2. **计费模式**: 腾讯混元按调用次数计费，请注意控制使用量
3. **网络要求**: 确保网络可以访问腾讯云 API 接口
4. **错误处理**: 项目已实现完善的错误处理机制，会在控制台显示详细错误信息

## 常见问题

### Q: 提示 "Secret Key 未正确配置"
A: 请检查 `.env` 文件中的 `HUNYUAN_SECRET_KEY` 是否正确设置

### Q: API 调用失败，提示认证错误
A: 请确认：
   - Secret ID 和 Secret Key 是否正确
   - 是否已开通混元大模型服务
   - 账户余额是否充足

### Q: 网络连接失败
A: 请检查：
   - 网络连接是否正常
   - 防火墙设置是否允许访问腾讯云 API
   - 是否需要配置代理

## 技术实现

- 使用官方腾讯云 SDK 进行 API 签名
- 支持异步调用，提高并发性能
- 实现完善的错误处理和重试机制
- 自动消息格式转换，兼容项目消息格式

## 相关链接

- [腾讯混元官方文档](https://cloud.tencent.com/document/product/1729)
- [API 接口文档](https://cloud.tencent.com/document/api/1729/105701)
- [腾讯云控制台](https://console.cloud.tencent.com/)
