from typing import Any, Dict

from domain.model.board import Board
from domain.model.current_game import CurrentGame
from web.model.web_board import WebBoard
from web.model.web_game import WebGame


class WebCurrentGameMapper:
    @staticmethod
    def board_from_payload(payload: Dict[str, Any]) -> Board:
        if not isinstance(payload, dict):
            raise ValueError("Request body must be a JSON object.")

        if "board" not in payload or not isinstance(payload["board"], dict):
            raise ValueError("Request body must include board.")
        if "cells" not in payload["board"]:
            raise ValueError("Board must include cells.")

        return Board(cells=payload["board"]["cells"])

    @staticmethod
    def from_domain(game: CurrentGame) -> WebGame:
        return WebGame(
            game_id=str(game.game_id),
            board=WebBoard(cells=[row[:] for row in game.board.cells]),
        )

    @staticmethod
    def to_dict(web_game: WebGame) -> Dict[str, Any]:
        return {
            "game_id": web_game.game_id,
            "board": {
                "cells": [row[:] for row in web_game.board.cells],
            },
        }
