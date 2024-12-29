from typing import Dict, List

from fastapi import WebSocket
from app.RoomState import RoomState


class RoomManager:
    def __init__(self):
        self.rooms: Dict[str, RoomState] = {}

    async def connect(self, room_id: str, websocket: WebSocket):
        if room_id not in self.rooms:
            self.rooms[room_id] = RoomState(room_id)
        await self.rooms[room_id].add_connection(websocket)

    def disconnect(self, room_id: str, websocket: WebSocket):
        if room_id in self.rooms:
            self.rooms[room_id].remove_connection(websocket)

    async def handle_message(self, room_id: str, websocket: WebSocket, raw_data: dict):
        if room_id in self.rooms:
            await self.rooms[room_id].process_message(raw_data)
