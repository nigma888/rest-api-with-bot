from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    Form,
    HTTPException,
    Header,
    status,
    WebSocket,
    WebSocketDisconnect,
)
from db.database import get_session
from sqlalchemy.orm import Session

from config import Config

from typing import List, Dict

from externals.userRole import UserRole

from db import crud

import json

from .. import schemas


router = APIRouter(tags=["tag"])


class ConnectionManager:
    def __init__(self):
        self.connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.connections.remove(websocket)

    async def broadcast(self, data: str):
        for connection in self.connections:
            await connection.send_text(data)


manager = ConnectionManager()


@router.websocket("/ws/article")
async def websocket(websocket: WebSocket):
    # query = users.select().where(users_cboxes_relation.c.token == ws_token)
    # user = await database.fetch_one(query=query)
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            token, id, date = data.split(";")
            if token == Config.SECRET_TOKEN_WS:
                await manager.broadcast(
                    json.dumps(
                        {
                            "type": "CreateNewUser",
                            "id": id,
                            "TimeStamp": date,
                        }
                    )
                )
    except:
        manager.disconnect(websocket)
