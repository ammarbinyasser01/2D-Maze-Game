class Player:
    def __init__(self):
        self.x = 1
        self.y = 1
        self.moves = 0
        self.collisions = 0

    def move(self, dx, dy, grid):
        """Attempt to move by (dx, dy).

        Returns True if the move succeeded, False if it hit a wall.
        """
        nx = self.x + dx
        ny = self.y + dy

        if grid[ny][nx] == 0:          # open cell → move
            self.x = nx
            self.y = ny
            self.moves += 1
            return True
        else:                           # wall → collision
            self.collisions += 1
            return False