import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import init_db
from app.api.companions import router as companions_router
from app.api.chat import router as chat_router
from app.api.chat_sessions import router as sessions_router
import socketio

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    print("🚀 AI灵魂伙伴 v1.0.0 启动中...")
    
    # 初始化数据库
    await init_db()
    print("✓ 数据库初始化完成")
    
    yield
    
    print("👋 AI灵魂伙伴正在关闭...")

# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(companions_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(sessions_router, prefix="/api")

# 创建 Socket.IO 服务器
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=settings.allowed_origins_list,
    logger=settings.DEBUG,
    engineio_logger=settings.DEBUG
)

# 注册聊天引擎事件处理器
from app.services.chat_engine import register_socketio_events
register_socketio_events(sio)

# 创建 Socket.IO ASGI 应用
socket_app = socketio.ASGIApp(sio, app)

@app.get("/")
async def read_root():
    return {
        "message": "AI灵魂伙伴 API",
        "version": settings.APP_VERSION,
        "features": {
            "websocket": True,
            "streaming": True,
            "llm_provider": settings.LLM_PROVIDER
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ai-companion-backend"}
