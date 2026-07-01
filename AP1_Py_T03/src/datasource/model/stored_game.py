from dataclasses import dataclass
from uuid import UUID

from datasource.model.stored_board import StoredBoard


@dataclass
class StoredGame:
    game_id: UUID
    board: StoredBoard
