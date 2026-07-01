from dataclasses import dataclass
from typing import List


@dataclass
class StoredBoard:
    cells: List[List[int]]
