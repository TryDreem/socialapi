from fastapi import APIRouter,Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.websockets import WebSocket, WebSocketDisconnect
from app.core.security import decode_access_token
from app.database import get_db
from app.models.user import User
from sqlalchemy import select
from app.core.websocket_manager import manager
import logging


logger = logging.getLogger(__name__)
router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(
        websocket: WebSocket,
        token: str,
        db: AsyncSession = Depends(get_db)
):
    email = decode_access_token(token)

    query = select(User).where(User.email == email)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        logger.warning(f"User {email} not found")
        await websocket.close(code=1008)
        return

    await manager.connect(user.id, websocket)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(user.id)

    return


