from dataclasses import dataclass
from typing import List


@dataclass
class WebBoard:
    cells: List[List[int]]
