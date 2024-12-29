import random
from typing import Callable, Dict, List, Optional, Union
from fastapi import WebSocket
from app.logger import logger
from app.models import Player
from app.Message import BaseMessage, JoinMessage, StartGameMessage, MESSAGE_CLASSES


class RoomState:
    def __init__(self, room_id: str):
        self.room_id = room_id
        self.players: List[Player] = []
        self.status = "waiting"  # "waiting" -> "active" -> "finished"
        self.deck: List[str] = [
            "6♥", "7♥", "8♥", "9♥", "10♥", "J♥", "Q♥", "K♥", "A♥",
            "6♠", "7♠", "8♠", "9♠", "10♠", "J♠", "Q♠", "K♠", "A♠",
            "6♦", "7♦", "8♦", "9♦", "10♦", "J♦", "Q♦", "K♦", "A♦",
            "6♣", "7♣", "8♣", "9♣", "10♣", "J♣", "Q♣", "K♣", "A♣"]
        self.trump_card: Optional[str] = None
        self.player_cards: Dict[str, List[str]] = []
        self.connections: List[Dict[str, Union[None, str, WebSocket]]] = []

        self.message_handlers: Dict[str, Callable[[BaseMessage], None]] = {}
        self.register_handlers()

    def get_player_connection(self, player_id: str) -> Optional[WebSocket]:
        """Возвращает WebSocket соединение игрока по его ID"""
        for connection in self.connections:
            if connection["player_id"] == player_id:
                return connection["websocket"]
        return None

    def register_handlers(self):
        """Регистрируем обработчики сообщений"""
        self.message_handlers = {
            "join": self.handle_join,
            "start_game": self.handle_start_game,
            "make_move": self.handle_make_move,
        }

    def assign_player_id(self, websocket: WebSocket, player_id: str):
        """Привязывает player_id к уже существующему WebSocket"""
        for connection in self.connections:
            if connection["websocket"] == websocket:
                if connection["player_id"] is not None:
                    raise ValueError("Этот WebSocket уже привязан к игроку")
                connection["player_id"] = player_id
                return
        raise ValueError("Соединение не найдено")

    async def process_message(self, websocket: WebSocket, raw_data: dict):
        logger.info(f"Message proccessing started in {self.room_id}")
        """Обрабатываем сообщение через зарегистрированные обработчики"""
        message_type = raw_data.get("type")
        if message_type not in self.message_handlers:
            logger.error(f"Unknown message type: {message_type}")
            raise ValueError(f"Unknown message type: {message_type}")

        # Преобразуем raw_data в Pydantic-класс
        message_class = MESSAGE_CLASSES.get(message_type)
        if not message_class:
            logger.error(f"Unknown Pydantic-класс for type {message_type}")
            raise ValueError(
                f"Unknown Pydantic-класс for type {message_type}")

        message = message_class(**raw_data)

        # Вызываем обработчик
        await self.message_handlers[message_type](websocket, message)

    async def handle_join(self, websocket: WebSocket, message: JoinMessage):
        player_id = message.player_id

        # Привязываем player_id к WebSocket
        self.assign_player_id(websocket, player_id)

        # Добавляем игрока в список
        new_player = Player(id=player_id)
        self.players.append(new_player)

        # Уведомляем остальных игроков
        await self.broadcast({
            "type": "player_joined",
            "player_id": player_id
        })

    async def handle_start_game(self, websocket: WebSocket, message: StartGameMessage):
        """Обрабатывает начало игры"""
        if self.status != "waiting":
            raise ValueError("Игра уже началась.")
        self.status = "active"

        # Генерация и перемешивание колоды
        random.shuffle(self.deck)

        # Раздача карт
        self.player_cards = {
            player.id: [self.deck.pop() for _ in range(6)]
            for player in self.players
        }
        self.trump_card = self.deck.pop()  # Последняя карта - козырь

        # Уведомляем всех игроков о начале игры и козыре
        await self.broadcast({
            "type": "game_started",
            "trump_card": self.trump_card
        })

        # Отправляем каждому игроку его карты
        for player in self.players:
            # Получаем WebSocket соединение для игрока
            player_connection = self.get_player_connection(player.id)
            if player_connection:
                await player_connection.send_json({
                    "type": "your_cards",
                    "cards": self.player_cards[player.id]
                })

    async def handle_make_move(self, data: dict):
        # Обработка хода
        # ...
        pass

    async def add_connection(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append({
            "websocket": websocket,
            "player_id": None
        })

    def remove_connection(self, websocket: WebSocket):
        self.connections = [
            conn for conn in self.connections if conn["websocket"] != websocket]

    async def broadcast(self, message: dict):
        """Отправка сообщения всем подключенным WebSocket"""
        for connection in self.connections:
            try:
                await connection["websocket"].send_json(message)
            except Exception as e:
                logger.error(f"Ошибка при отправке сообщения: {e}")
