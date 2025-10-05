"""
临时简化的main.py - 用于测试API阻塞问题
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.companions import router as companions_router

# 创建 FastAPI 应用
app = FastAPI(
    title="AI伙伴 API 测试",
    version="1.0.0",
    debug=True
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 只注册伙伴路由
app.include_router(companions_router, prefix="/api")

@app.get("/")
async def read_root():
    return {"message": "临时API测试", "status": "ok"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "test"}
