from fastapi import FastAPI
from app.database import engine
from sqlalchemy import text
from app.config import settings
from app.api import auth, posts
from app.core.logging_config import setup_logging

app = FastAPI(
    title="SocialAPI",
    description="REST API for microblogging",
    version="1.0.0",
    debug=settings.DEBUG
)

setup_logging()
app.include_router(auth.router)
app.include_router(posts.router)


@app.get("/")
async def root():
    return{
        "message" : "SocialAPI is running",
        "version": "1.0.0",
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

