from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Dict
from app.auth import get_current_user
from app import models
from app.database import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/ws", tags=["WebSocket"])

active_connections: Dict[int, WebSocket] = {}


@router.websocket("/notifications")
async def websocket_notifications(
    websocket: WebSocket,
    token: str,
    db: Session = Depends(get_db)
):
    # Авторизация по токену (передаётся в query params)
    from app.auth import decode_access_token
    user_data = decode_access_token(token)
    if not user_data:
        await websocket.close(code=1008)
        return

    user_id = user_data.get("user_id")
    await websocket.accept()
    active_connections[user_id] = websocket
    print(f"Пользователь {user_id} подключился к уведомлениям")

    try:
        while True:
            await websocket.receive_text()  # держим соединение открытым
    except WebSocketDisconnect:
        print(f"Пользователь {user_id} отключился")
        del active_connections[user_id]
