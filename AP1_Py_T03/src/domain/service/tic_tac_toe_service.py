from math import inf
from typing import Optional, Tuple
from uuid import UUID, uuid4

from datasource.repository.current_game_repository import CurrentGameRepository
from domain.model.board import AI_CELL, BOARD_SIZE, EMPTY_CELL, PLAYER_CELL, Board
from domain.model.current_game import CurrentGame
from domain.service.game_service import GameService


class TicTacToeService(GameService):
    def __init__(self, repository: CurrentGameRepository):
        self._repository = repository

    def create_game(self) -> CurrentGame:
        game = CurrentGame.empty(uuid4())
        self._repository.save(game)
        return game

    def process_turn(self, game_id: UUID, updated_board: Board) -> CurrentGame:
        previous_game = self._repository.get(game_id)
        if previous_game is None:
            raise LookupError("Game not found.")

        was_finished, _, _ = self.check_game_over(previous_game)
        if was_finished:
            raise ValueError("Game is already over.")

        updated_game = CurrentGame(game_id=game_id, board=updated_board)

        is_valid, message = self.validate_game_board(previous_game, updated_game)
        if not is_valid:
            raise ValueError(message)

        player_finished, _, _ = self.check_game_over(updated_game)
        result_game = updated_game

        if not player_finished:
            next_move = self.get_next_move(updated_game)
            if next_move is not None:
                result_game = CurrentGame(
                    game_id=updated_game.game_id,
                    board=updated_game.board.with_value(next_move[0], next_move[1], AI_CELL),
                )

        self._repository.save(result_game)
        return result_game

    def get_next_move(self, game: CurrentGame) -> Optional[Tuple[int, int]]:
        if self.check_game_over(game)[0]:
            return None

        empty_cells = game.board.empty_cells()
        if not empty_cells:
            return None

        if len(empty_cells) == BOARD_SIZE * BOARD_SIZE:
            return 1, 1

        best_score = -inf
        best_move: Optional[Tuple[int, int]] = None

        for row, column in empty_cells:
            candidate_board = game.board.with_value(row, column, AI_CELL)
            score = self._minimax(candidate_board, is_ai_turn=False, depth=0)
            if score > best_score:
                best_score = score
                best_move = (row, column)

        return best_move

    def validate_game_board(self, previous_game: CurrentGame, updated_game: CurrentGame) -> Tuple[bool, str]:
        changed_cells = []

        for row in range(BOARD_SIZE):
            for column in range(BOARD_SIZE):
                previous_value = previous_game.board.get_cell(row, column)
                updated_value = updated_game.board.get_cell(row, column)
                if previous_value != updated_value:
                    changed_cells.append((row, column, previous_value, updated_value))

        if len(changed_cells) != 1:
            return False, "Exactly one player move must be added to the board."

        row, column, previous_value, updated_value = changed_cells[0]
        if previous_value != EMPTY_CELL:
            return False, f"Cell ({row}, {column}) cannot be changed."

        if updated_value != PLAYER_CELL:
            return False, "The user move must use value 1."

        return True, "Board update is valid."

    def check_game_over(self, game: CurrentGame) -> Tuple[bool, Optional[int], str]:
        return self._evaluate_board(game.board)

    def _minimax(self, board: Board, is_ai_turn: bool, depth: int) -> int:
        is_finished, winner, _ = self._evaluate_board(board)
        if is_finished:
            if winner == AI_CELL:
                return 10 - depth
            if winner == PLAYER_CELL:
                return depth - 10
            return 0

        if is_ai_turn:
            best_score = -inf
            for row, column in board.empty_cells():
                score = self._minimax(
                    board.with_value(row, column, AI_CELL),
                    is_ai_turn=False,
                    depth=depth + 1,
                )
                best_score = max(best_score, score)
            return int(best_score)

        best_score = inf
        for row, column in board.empty_cells():
            score = self._minimax(
                board.with_value(row, column, PLAYER_CELL),
                is_ai_turn=True,
                depth=depth + 1,
            )
            best_score = min(best_score, score)
        return int(best_score)

    @staticmethod
    def _evaluate_board(board: Board) -> Tuple[bool, Optional[int], str]:
        lines = []

        for index in range(BOARD_SIZE):
            lines.append([board.get_cell(index, column) for column in range(BOARD_SIZE)])
            lines.append([board.get_cell(row, index) for row in range(BOARD_SIZE)])

        lines.append([board.get_cell(index, index) for index in range(BOARD_SIZE)])
        lines.append([board.get_cell(index, BOARD_SIZE - index - 1) for index in range(BOARD_SIZE)])

        for line in lines:
            if line[0] != EMPTY_CELL and all(value == line[0] for value in line):
                winner = line[0]
                return True, winner, f"Winner is {'player' if winner == PLAYER_CELL else 'computer'}."

        if board.is_full():
            return True, None, "Draw."

        return False, None, "Game is not finished."
