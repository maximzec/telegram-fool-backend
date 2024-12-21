from fastapi import WebSocket
from app.models import RoomState, Player
from typing import Dict, List
import uuid
from .logger import logger


class RoomManager:
    def __init__(self):
        self.rooms: Dict[str, RoomState] = {}
        self.connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, room_id: str, websocket: WebSocket):
        await websocket.accept()
        logger.info(f"Подключение к комнате {room_id}")
        if room_id not in self.rooms:
            # Инициализация новой комнаты
            logger.info(f"Создание комнаты: {room_id}")
            self.rooms[room_id] = RoomState()
            self.connections[room_id] = []
            logger.info(f"Комната создана: {room_id}")
        self.connections[room_id].append(websocket)
        await self.broadcast(room_id, {"type": "user_connected", "message": f"New user connected to room {room_id}"})
        logger.info(f"Подключён новый игрок в комнату {room_id}")

    def disconnect(self, room_id: str, websocket: WebSocket):
        if room_id in self.connections:
            self.connections[room_id].remove(websocket)
            print(f"Игрок отключился из комнаты {room_id}")

    async def handle_message(self, room_id: str, websocket: WebSocket, data: dict):
        if room_id not in self.rooms:
            self.rooms[room_id] = RoomState()
            self.connections[room_id] = []
            return

        # Пример обработки сообщений
        if data["type"] == "join":
            player_id = data.get("player_id", str(uuid.uuid4()))
            player = Player(id=player_id)
            self.rooms[room_id].players.append(player)
            await self.broadcast(room_id, {"type": "player_joined", "player_id": player_id})

        elif data["type"] == "start_game":
            self.rooms[room_id].status = "active"
            await self.broadcast(room_id, {"type": "game_started", "state": self.rooms[room_id].dict()})

    async def broadcast(self, room_id: str, message: dict):
        if room_id in self.connections:
            for connection in self.connections[room_id]:
                await connection.send_json(message)
