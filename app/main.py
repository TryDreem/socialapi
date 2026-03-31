from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.posts import feed_router
from app.core.rate_limit import limiter
from app.database import engine
from sqlalchemy import text
from app.config import settings
from app.api import auth, posts, comments, likes, follows, notifications, websockets
from app.core.logging_config import setup_logging

app = FastAPI(
    title="SocialAPI",
    description="REST API for microblogging",
    version="1.0.0",
    debug=settings.DEBUG
)


app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
setup_logging()

all_routers = [
    auth.router,
    posts.router,
    comments.router,
    likes.router,
    follows.router,
    feed_router,
    notifications.router,
    websockets.router,
]

for router in all_routers:
    app.include_router(router)


@app.get("/")
async def root():
    return{
        "message" : "SocialAPI is running",
        "version": "1.x.x",
        "environment": settings.ENV_STATE,
    }

@app.get("/health")
async def health_check():
    return {
        "status" : "ok"
    }



@app.get("/db-check")
async def database_check():
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {
            "database": "connected",
            "status": "ok"
        }
    except Exception as e:
        return {
            "database": "error",
            "status": "failed",
            "error": str(e)
        }

