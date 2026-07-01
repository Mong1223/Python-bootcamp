from dataclasses import dataclass

from web.model.web_board import WebBoard


@dataclass
class WebGame:
    game_id: str
    board: WebBoard
