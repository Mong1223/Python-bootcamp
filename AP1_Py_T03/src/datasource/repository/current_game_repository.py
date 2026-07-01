from typing import Optional
from uuid import UUID

from datasource.mapper.current_game_mapper import CurrentGameMapper
from datasource.model.game_state_storage import GameStateStorage
from domain.model.current_game import CurrentGame


class CurrentGameRepository:
    def __init__(self, storage: GameStateStorage):
        self._storage = storage
        self._mapper = CurrentGameMapper()

    def save(self, game: CurrentGame) -> None:
        self._storage.save(self._mapper.to_datasource(game))

    def get(self, game_id: UUID) -> Optional[CurrentGame]:
        stored_game = self._storage.get(game_id)
        if stored_game is None:
            return None
        return self._mapper.to_domain(stored_game)
