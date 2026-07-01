from dataclasses import dataclass
from typing import List, Tuple


BOARD_SIZE = 3
EMPTY_CELL = 0
PLAYER_CELL = 1
AI_CELL = 2
VALID_CELL_VALUES = {EMPTY_CELL, PLAYER_CELL, AI_CELL}


@dataclass
class Board:
    cells: List[List[int]]

    def __post_init__(self) -> None:
        if len(self.cells) != BOARD_SIZE:
            raise ValueError(f"Board must be {BOARD_SIZE}x{BOARD_SIZE}.")

        for row in self.cells:
            if len(row) != BOARD_SIZE:
                raise ValueError(f"Board must be {BOARD_SIZE}x{BOARD_SIZE}.")
            for value in row:
                if value not in VALID_CELL_VALUES:
                    raise ValueError("Cell values must be 0, 1, or 2.")

    @classmethod
    def empty(cls) -> "Board":
        return cls([[EMPTY_CELL] * BOARD_SIZE for _ in range(BOARD_SIZE)])

    def get_cell(self, row: int, column: int) -> int:
        self._validate_position(row, column)
        return self.cells[row][column]

    def empty_cells(self) -> List[Tuple[int, int]]:
        result: List[Tuple[int, int]] = []
        for row in range(BOARD_SIZE):
            for column in range(BOARD_SIZE):
                if self.cells[row][column] == EMPTY_CELL:
                    result.append((row, column))
        return result

    def is_full(self) -> bool:
        return not self.empty_cells()

    def with_value(self, row: int, column: int, value: int) -> "Board":
        self._validate_position(row, column)
        if value not in VALID_CELL_VALUES:
            raise ValueError("Cell values must be 0, 1, or 2.")
        if self.cells[row][column] != EMPTY_CELL:
            raise ValueError("Cell is already taken.")

        copied_cells = [current_row[:] for current_row in self.cells]
        copied_cells[row][column] = value
        return Board(copied_cells)

    @staticmethod
    def _validate_position(row: int, column: int) -> None:
        if not 0 <= row < BOARD_SIZE or not 0 <= column < BOARD_SIZE:
            raise ValueError("Cell position is out of bounds.")
