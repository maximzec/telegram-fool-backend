from pydantic import BaseModel


class BaseMessage(BaseModel):
    type: str  # Тип сообщения

# Сообщение для присоединения к комнате


class JoinMessage(BaseMessage):
    type: str = "join"
    player_id: str

# Сообщение для начала игры


class StartGameMessage(BaseMessage):
    type: str = "start_game"

# Сообщение для хода


class MakeMoveMessage(BaseMessage):
    type: str = "make_move"
    move: str  # Ход, например, карта "6♠"


# Словарь для маппинга типов сообщений к Pydantic-моделям
MESSAGE_CLASSES = {
    "join": JoinMessage,
    "start_game": StartGameMessage,
    "make_move": MakeMoveMessage,
}
