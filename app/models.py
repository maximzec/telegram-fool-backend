from typing import List, Dict
from pydantic import BaseModel


class Player(BaseModel):
    id: str


class RoomState(BaseModel):
    status: str = "waiting"  # waiting, active, finished
    players: List[Player] = []
    table: List[str] = []
    deck: List[str] = []
