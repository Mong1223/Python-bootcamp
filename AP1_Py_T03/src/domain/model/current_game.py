from dataclasses import dataclass
from uuid import UUID

from domain.model.board import Board


@dataclass
class CurrentGame:
    game_id: UUID
    board: Board

    @classmethod
    def empty(cls, game_id: UUID) -> "CurrentGame":
        return cls(game_id=game_id, board=Board.empty())
