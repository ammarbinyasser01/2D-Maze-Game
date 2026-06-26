import random


class Maze:
    """Recursive-backtracker maze generator.

    Grid convention:
        1 = wall
        0 = open path
    """

    def __init__(self, rows, cols):
        # Ensure odd dimensions so the algorithm works cleanly
        self.rows = rows if rows % 2 == 1 else rows + 1
        self.cols = cols if cols % 2 == 1 else cols + 1

    def generate(self):
        grid = [[1] * self.cols for _ in range(self.rows)]

        # Carve from (1, 1)
        self._carve(grid, 1, 1)

        # Guarantee entrance and exit are open
        grid[1][1] = 0
        grid[self.rows - 2][self.cols - 2] = 0

        return grid

    def _carve(self, grid, x, y):
        grid[y][x] = 0
        directions = [(0, -2), (0, 2), (-2, 0), (2, 0)]
        random.shuffle(directions)

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if (
                0 < nx < self.cols - 1
                and 0 < ny < self.rows - 1
                and grid[ny][nx] == 1
            ):
                grid[y + dy // 2][x + dx // 2] = 0   # knock out wall
                self._carve(grid, nx, ny)