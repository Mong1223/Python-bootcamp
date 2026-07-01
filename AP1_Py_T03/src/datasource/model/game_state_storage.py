from threading import Lock
from typing import Dict, Optional
from uuid import UUID

from datasource.model.stored_game import StoredGame


class GameStateStorage:
    def __init__(self) -> None:
        self._games: Dict[UUID, StoredGame] = {}
        self._lock = Lock()

    def save(self, game: StoredGame) -> None:
        with self._lock:
            self._games[game.game_id] = game

    def get(self, game_id: UUID) -> Optional[StoredGame]:
        with self._lock:
            return self._games.get(game_id)
