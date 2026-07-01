from abc import ABC, abstractmethod
from typing import Optional, Tuple

from domain.model.board import Board
from domain.model.current_game import CurrentGame


class GameService(ABC):
    @abstractmethod
    def create_game(self) -> CurrentGame:
        raise NotImplementedError

    @abstractmethod
    def get_next_move(self, game: CurrentGame) -> Optional[Tuple[int, int]]:
        raise NotImplementedError

    @abstractmethod
    def validate_game_board(self, previous_game: CurrentGame, updated_game: CurrentGame) -> Tuple[bool, str]:
        raise NotImplementedError

    @abstractmethod
    def process_turn(self, game_id, updated_board: Board) -> CurrentGame:
        raise NotImplementedError

    @abstractmethod
    def check_game_over(self, game: CurrentGame) -> Tuple[bool, Optional[int], str]:
        raise NotImplementedError
