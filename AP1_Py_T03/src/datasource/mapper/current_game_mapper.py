from datasource.model.stored_board import StoredBoard
from datasource.model.stored_game import StoredGame
from domain.model.board import Board
from domain.model.current_game import CurrentGame


class CurrentGameMapper:
    @staticmethod
    def to_datasource(game: CurrentGame) -> StoredGame:
        return StoredGame(
            game_id=game.game_id,
            board=StoredBoard(cells=[row[:] for row in game.board.cells]),
        )

    @staticmethod
    def to_domain(stored_game: StoredGame) -> CurrentGame:
        return CurrentGame(
            game_id=stored_game.game_id,
            board=Board(cells=[row[:] for row in stored_game.board.cells]),
        )
