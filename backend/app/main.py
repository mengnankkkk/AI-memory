import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import init_db
from app.api.companions import router as companions_router
from app.api.chat import router as chat_router
from app.api.chat_sessions import router as sessions_router
from app.api.ab_test import router as ab_test_router
from app.api.config import router as config_router
from app.api.export import router as export_router
from app.api.notification import router as notification_router
from app.api.stats import router as stats_router
from app.api.romance import router as romance_router
from app.api.auth import router as auth_router  # 用户认证路由
from app.api.offline_life import router as offline_life_router  # 离线生活路由
from app.services.timeline_scheduler import timeline_scheduler  # 时间线调度器
import socketio

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    print("[STARTUP] AI灵魂伙伴 v1.0.0 启动中...")

    # 初始化数据库
    await init_db()
    print("[OK] 数据库初始化完成")

    # 启动时间线调度器
    await timeline_scheduler.start()
    print("[OK] 时间线调度器已启动")

    yield

    # 停止时间线调度器
    await timeline_scheduler.stop()
    print("[SHUTDOWN] AI灵魂伙伴正在关闭...")

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
app.include_router(auth_router, prefix="/api")  # 认证路由（需要最先注册）
app.include_router(companions_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(sessions_router, prefix="/api")
app.include_router(ab_test_router, prefix="/api")
app.include_router(config_router, prefix="/api")
app.include_router(export_router, prefix="/api")
app.include_router(notification_router, prefix="/api")
app.include_router(stats_router, prefix="/api")
app.include_router(romance_router, prefix="/api")
app.include_router(offline_life_router, prefix="/api")  # 离线生活路由

# 创建 Socket.IO 服务器
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=settings.allowed_origins_list,
    logger=settings.DEBUG,
    engineio_logger=settings.DEBUG,
    compression=True,  # 启用压缩
    engineio_options={
        'compression': True,
        'perMessageDeflate': True
    }
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
