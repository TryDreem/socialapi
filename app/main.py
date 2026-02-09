from fastapi import FastAPI
from app.config import settings

app = FastAPI(
    title="SocialAPI",
    description="REST API for microblogging",
    version="1.0.0",
    debug=settings.DEBUG
)


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


