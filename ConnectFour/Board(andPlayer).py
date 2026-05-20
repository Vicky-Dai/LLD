from typing import Optional, List
from enum import Enum
class DiscColor(Enum):
    Red = "red"
    Green = "green"

class Board:
    def __init__(self, rows = 6, cols=7):
        self.rows = rows
        self.cols = cols
        self.grid = list[list[Optional[DiscColor]]] = [[None]*(cols)for _ in range(rows)] #This represents a 2D grid where each cell can either contain a DiscColor or be empty (None).
        # [None for _ in range(cols)] for _ in range(rows)]这样也行

    def canPlace(self, column)->bool:
        if column < 0 or column >= self.cols:
            return False
        return self.grid[0][column] is None #!!!!!

    def placeDisc(self, column, color)->int:
        if self.canPlace(column) is None:
            return -1
        for row in range(self.rows-1, -1, -1):
            if self.grid[row][column] is None:
                self.grid[row][column] = color
                return row
        return -1 #!!!!!!!

    def check_win(self, row:int, column:int, color:DiscColor) -> bool:
        # check inside the board
        # check 8 directions
        # if 4 continuous sme color, wins, return True
        if not self.in_bounds():
            raise ValueError(f"Out of bounds")
        if self.board[row][column] != color:
            raise ValueError(f"Wrong color {color}")
        dirs = [[0, 1], [1, 0], [1, 1], [1, -1]]
        for dr, dc in dirs:
            count = 1
            count += self._count_in_direction(row, column, dr, dc)
            count += self._count_in_direction(row, column, -dr, -dc)
            if count >= 4:
                return True
        return False

    # def _count_in_direction(self, row, col, dr, dc):
    #     count = 0
    #     while True:
    #         if self._in_bounds(row, col) and self.board[row+dr][col+dc] == self.board[row][col]:
    #             count += 1
    #             row += dr
    #             col += dc
    #         else:
    #             break
    #     return count
    def _count_in_direction( # !!!! 这种写法就更好 边界检查更清楚 不会重复读源点
        self, row: int, column: int, dr: int, dc: int, color: DiscColor
    ) -> int:
        count = 0
        r = row + dr
        c = column + dc
        while self._in_bounds(r, c) and self.grid[r][c] == color:
            count += 1
            r += dr
            c += dc
        return count

    def in_bounds(self, row, column) -> bool:
        if 0<=row <self.rows and 0<=column<self.cols:
            return True
        return False


class Player:
    def __init__(self, name, color:DiscColor):
        self.name = name
        self.color = color