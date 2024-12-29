from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from app.RoomManager import RoomManager

app = FastAPI()

# Менеджер для управления комнатами
room_manager = RoomManager()


@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    await room_manager.connect(room_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            await room_manager.handle_message(room_id, websocket, data)
    except WebSocketDisconnect:
        room_manager.disconnect(room_id, websocket)
