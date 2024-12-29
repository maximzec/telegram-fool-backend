from typing import List, Dict, Optional
from pydantic import BaseModel


class Player(BaseModel):
    id: str
