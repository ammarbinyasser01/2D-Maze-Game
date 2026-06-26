import pygame
import time
import random

from settings import *
from maze_generator import Maze
from player import Player
from leaderboard import save_score, is_new_highscore, get_scores
import sounds


# ─────────────────────────────────────────────────────────
#  Utility helpers
# ─────────────────────────────────────────────────────────

def draw_rounded_rect(surface, colour, rect, radius=12, border=0, border_colour=None):
    pygame.draw.rect(surface, colour, rect, border_radius=radius)
    if border and border_colour:
        pygame.draw.rect(surface, border_colour, rect, border, border_radius=radius)


def make_button(surface, text, rect, font,
                bg=(60, 60, 120), fg=WHITE,
                hover_bg=(90, 90, 180), border_colour=PANEL_BORDER,
                mouse_pos=None):
    """Draw a button and return True if the mouse is hovering over it."""
    hovered = rect.collidepoint(mouse_pos) if mouse_pos else False
    colour = hover_bg if hovered else bg
    draw_rounded_rect(surface, colour, rect, radius=10, border=2, border_colour=border_colour)
    label = font.render(text, True, fg)
    lx = rect.centerx - label.get_width() // 2
    ly = rect.centery - label.get_height() // 2
    surface.blit(label, (lx, ly))
    return hovered


# ─────────────────────────────────────────────────────────
#  Texture surfaces (generated once per cell_size change)
# ─────────────────────────────────────────────────────────

class TextureCache:
    def __init__(self):
        self._cs = None
        self.road_h   = None   # horizontal road tile
        self.road_v   = None   # vertical road tile
        self.road_c   = None   # crossing / plain road tile
        self.grass    = None   # grass / wall tile

    def build(self, cell_size):
        if cell_size == self._cs:
            return
        self._cs = cell_size
        cs = cell_size

        # ── grass tile (wall cells) ─────────────────────
        grass = pygame.Surface((cs, cs))
        grass.fill(DARK_GREEN)
        rng = random.Random(42)
        for _ in range(cs * cs // 6):
            bx = rng.randint(0, cs - 1)
            by = rng.randint(0, cs - 1)
            shade = rng.randint(0, 30)
            c = (20 + shade, 90 + shade, 20 + shade)
            grass.set_at((bx, by), c)
        # small tree-dot clusters
        for _ in range(max(1, cs // 12)):
            tx = rng.randint(2, cs - 3)
            ty = rng.randint(2, cs - 3)
            pygame.draw.circle(grass, (10, 60, 10), (tx, ty), max(2, cs // 14))
        self.grass = grass

        # ── road base (path cells) ─────────────────────
        def _road_base():
            surf = pygame.Surface((cs, cs))
            surf.fill(ROAD_MID)
            # subtle grain
            rng2 = random.Random(7)
            for _ in range(cs * cs // 8):
                px = rng2.randint(0, cs - 1)
                py = rng2.randint(0, cs - 1)
                v = rng2.randint(-12, 12)
                base = ROAD_MID
                c = (
                    max(0, min(255, base[0] + v)),
                    max(0, min(255, base[1] + v)),
                    max(0, min(255, base[2] + v)),
                )
                surf.set_at((px, py), c)
            return surf

        # horizontal dashes down the centre
        road_h = _road_base()
        stripe_w = max(2, cs // 5)
        stripe_h = max(1, cs // 8)
        sy = cs // 2 - stripe_h // 2
        for sx in range(0, cs, stripe_w * 2):
            pygame.draw.rect(road_h, STRIPE_WHITE, (sx, sy, stripe_w, stripe_h))
        self.road_h = road_h

        # vertical dashes
        road_v = _road_base()
        sx2 = cs // 2 - stripe_h // 2
        for sy2 in range(0, cs, stripe_w * 2):
            pygame.draw.rect(road_v, STRIPE_WHITE, (sx2, sy2, stripe_h, stripe_w))
        self.road_v = road_v

        # plain crossing (intersections / short corridors)
        self.road_c = _road_base()

_textures = TextureCache()


def _road_tile(grid, x, y, rows, cols):
    """Choose which road tile to draw based on neighbours."""
    def open_(nx, ny):
        if 0 <= nx < cols and 0 <= ny < rows:
            return grid[ny][nx] == 0
        return False

    left  = open_(x - 1, y)
    right = open_(x + 1, y)
    up    = open_(x, y - 1)
    down  = open_(x, y + 1)

    h = left or right
    v = up or down

    if h and not v:
        return _textures.road_h
    if v and not h:
        return _textures.road_v
    return _textures.road_c


# ─────────────────────────────────────────────────────────
#  Popup helpers
# ─────────────────────────────────────────────────────────

def _popup_background(screen):
    """Darken the whole screen for modal popups."""
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    screen.blit(overlay, (0, 0))


# ─────────────────────────────────────────────────────────
#  Highscore table screen
# ─────────────────────────────────────────────────────────

def show_highscore_screen(screen, difficulty, clock):
    """Block until the player presses a button."""
    font_title = pygame.font.SysFont(None, 52)
    font_head  = pygame.font.SysFont(None, 32)
    font_row   = pygame.font.SysFont(None, 28)
    font_btn   = pygame.font.SysFont(None, 30)

    W, H = screen.get_size()
    btn_back = pygame.Rect(W // 2 - 100, H - 70, 200, 44)
    btn_menu = pygame.Rect(W // 2 - 100, H - 118, 200, 44)

    while True:
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "menu"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_back.collidepoint(mouse):
                    return "restart"
                if btn_menu.collidepoint(mouse):
                    return "menu"

        screen.fill((15, 15, 30))

        title = font_title.render(
            f"Highscores – {difficulty.capitalize()}", True, GOLD
        )
        screen.blit(title, (W // 2 - title.get_width() // 2, 30))

        # Column headers
        cols_x = [80, 250, 430, 580]
        headers = ["#", "Player", "Time", "Hits"]
        for hx, ht in zip(cols_x, headers):
            h_surf = font_head.render(ht, True, STRIPE_WHITE)
            screen.blit(h_surf, (hx, 100))

        pygame.draw.line(screen, PANEL_BORDER, (60, 130), (W - 60, 130), 2)

        scores = get_scores(difficulty)
        for i, entry in enumerate(scores[:10]):
            y = 145 + i * 34
            colour = GOLD if i == 0 else (WHITE if i < 3 else GRAY)
            m = int(entry["time"] // 60)
            s = int(entry["time"] % 60)
            ms = int((entry["time"] * 1000) % 1000)
            row_data = [
                f"{i + 1}",
                entry["name"][:14],
                f"{m:02}:{s:02}:{ms:03}",
                str(entry["collisions"]),
            ]
            for rx, rd in zip(cols_x, row_data):
                cell = font_row.render(rd, True, colour)
                screen.blit(cell, (rx, y))

        make_button(screen, "Play Again", btn_back, font_btn, mouse_pos=mouse)
        make_button(screen, "Main Menu",  btn_menu, font_btn, mouse_pos=mouse,
                    bg=(100, 40, 40), hover_bg=(160, 60, 60))

        pygame.display.flip()
        clock.tick(60)


# ─────────────────────────────────────────────────────────
#  Game class
# ─────────────────────────────────────────────────────────

class Game:
    def __init__(self, screen, player_name, difficulty):
        self.screen      = screen
        self.player_name = player_name
        self.difficulty  = difficulty
        self.clock       = pygame.time.Clock()

        # Difficulty config
        cfg = {
            "easy":   (EASY_ROWS,   EASY_COLS,   EASY_CELL),
            "medium": (MEDIUM_ROWS, MEDIUM_COLS, MEDIUM_CELL),
            "hard":   (HARD_ROWS,   HARD_COLS,   HARD_CELL),
        }
        self.rows, self.cols, self.cell_size = cfg.get(difficulty, cfg["easy"])

        _textures.build(self.cell_size)

        maze_w = self.cols * self.cell_size
        maze_h = self.rows * self.cell_size
        need_w = maze_w + STATS_WIDTH
        need_h = max(maze_h, 600)

        if screen.get_size() != (need_w, need_h):
            self.screen = pygame.display.set_mode((need_w, need_h))

        pygame.display.set_caption("2D Maze Game")

        # Fonts
        self.font_sm  = pygame.font.SysFont(None, 26)
        self.font_md  = pygame.font.SysFont(None, 32)
        self.font_lg  = pygame.font.SysFont(None, 50)
        self.font_xl  = pygame.font.SysFont(None, 64)

        self.new_game()

    # ── state ────────────────────────────────────────────

    def new_game(self):
        _textures.build(self.cell_size)
        self.maze  = Maze(self.rows, self.cols)
        self.grid  = self.maze.generate()
        self.player = Player()
        self.goal_x = self.cols - 2
        self.goal_y = self.rows - 2
        self.start_time  = time.time()
        self.game_won    = False
        self.game_over   = False
        self.new_hs      = False
        self.elapsed_final = 0.0
        self._popup_shown   = False   # guard: only show popup once

    # ── drawing ──────────────────────────────────────────

    def _offset_y(self):
        maze_h = self.rows * self.cell_size
        return (self.screen.get_height() - maze_h) // 2

    def _draw_maze(self, off_y):
        cs  = self.cell_size
        for y in range(self.rows):
            for x in range(self.cols):
                rect = pygame.Rect(x * cs, off_y + y * cs, cs, cs)
                if self.grid[y][x] == 1:
                    self.screen.blit(_textures.grass, rect)
                else:
                    tile = _road_tile(self.grid, x, y, self.rows, self.cols)
                    self.screen.blit(tile, rect)

    def _draw_player(self, off_y):
        cs = self.cell_size
        cx = self.player.x * cs + cs // 2
        cy = off_y + self.player.y * cs + cs // 2
        r  = max(4, cs // 2 - 3)
        pygame.draw.circle(self.screen, BLUE, (cx, cy), r)
        pygame.draw.circle(self.screen, WHITE, (cx, cy), r, 2)

    def _draw_goal(self, off_y):
        cs = self.cell_size
        rect = pygame.Rect(
            self.goal_x * cs + 2,
            off_y + self.goal_y * cs + 2,
            cs - 4, cs - 4
        )
        pygame.draw.rect(self.screen, GREEN, rect, border_radius=4)
        star = self.font_sm.render("★", True, YELLOW)
        self.screen.blit(
            star,
            (rect.centerx - star.get_width() // 2,
             rect.centery - star.get_height() // 2)
        )

    def _draw_panel(self):
        W, H = self.screen.get_size()
        panel_x = self.cols * self.cell_size
        panel_rect = pygame.Rect(panel_x, 0, STATS_WIDTH, H)
        pygame.draw.rect(self.screen, PANEL_BG, panel_rect)
        pygame.draw.line(self.screen, PANEL_BORDER, (panel_x, 0), (panel_x, H), 2)

        sx = panel_x + 16
        mouse = pygame.mouse.get_pos()

        def txt(text, y, colour=WHITE, font=None):
            f = font or self.font_sm
            s = f.render(text, True, colour)
            self.screen.blit(s, (sx, y))

        txt("2D MAZE", 18, GOLD, self.font_lg)
        pygame.draw.line(self.screen, PANEL_BORDER, (sx, 62), (W - 10, 62), 1)

        txt(f"Player:  {self.player_name}", 76)
        txt(f"Level:   {self.difficulty.capitalize()}", 104)

        # timer
        if self.game_won or self.game_over:
            elapsed = self.elapsed_final
        else:
            elapsed = time.time() - self.start_time

        m  = int(elapsed // 60)
        s  = int(elapsed % 60)
        ms = int((elapsed * 1000) % 1000)
        txt(f"Time:    {m:02}:{s:02}:{ms:03}", 132, YELLOW)
        txt(f"Moves:   {self.player.moves}",      160)

        col_colour = RED if self.player.collisions >= MAX_COLLISIONS else WHITE
        txt(f"Hits:    {self.player.collisions}/{MAX_COLLISIONS}", 188, col_colour)

        pygame.draw.line(self.screen, PANEL_BORDER, (sx, 218), (W - 10, 218), 1)

        # ── buttons ────────────────────────────────────
        bw, bh = STATS_WIDTH - 32, 38
        bx = sx

        # Restart
        self._btn_restart = pygame.Rect(bx, 228, bw, bh)
        make_button(self.screen, "↺  Restart (R)", self._btn_restart,
                    self.font_sm, mouse_pos=mouse)

        # Quit to menu
        self._btn_menu = pygame.Rect(bx, 274, bw, bh)
        make_button(self.screen, "⏎  Main Menu (Q)", self._btn_menu,
                    self.font_sm, bg=(100, 40, 40), hover_bg=(160, 60, 60),
                    mouse_pos=mouse)

        # Highscores (always visible)
        self._btn_hs = pygame.Rect(bx, 320, bw, bh)
        make_button(self.screen, "🏆  Highscores (H)", self._btn_hs,
                    self.font_sm, bg=(60, 100, 40), hover_bg=(90, 150, 60),
                    mouse_pos=mouse)

        # Controls reminder
        txt("Arrow keys to move", H - 60, DARK_GRAY)
        txt("Avoid walls — 3 hits = game over!", H - 38, RED)

    def _draw_gameover_popup(self):
        _popup_background(self.screen)
        W, H = self.screen.get_size()
        pw, ph = 380, 240
        px, py = (W - pw) // 2, (H - ph) // 2
        box = pygame.Rect(px, py, pw, ph)
        draw_rounded_rect(self.screen, (40, 10, 10), box, radius=16,
                          border=3, border_colour=RED)

        mouse = pygame.mouse.get_pos()

        t = self.font_xl.render("GAME OVER", True, RED)
        self.screen.blit(t, (px + pw // 2 - t.get_width() // 2, py + 20))

        sub = self.font_sm.render("Too many wall collisions!", True, WHITE)
        self.screen.blit(sub, (px + pw // 2 - sub.get_width() // 2, py + 90))

        bw, bh = 140, 40
        self._popup_restart = pygame.Rect(px + 30,        py + ph - 70, bw, bh)
        self._popup_quit    = pygame.Rect(px + pw - 170,  py + ph - 70, bw, bh)

        make_button(self.screen, "Restart", self._popup_restart, self.font_md,
                    mouse_pos=mouse)
        make_button(self.screen, "Main Menu", self._popup_quit, self.font_md,
                    bg=(100, 40, 40), hover_bg=(160, 60, 60), mouse_pos=mouse)

    def _draw_win_popup(self):
        _popup_background(self.screen)
        W, H = self.screen.get_size()
        pw, ph = 420, 300
        px, py = (W - pw) // 2, (H - ph) // 2
        box = pygame.Rect(px, py, pw, ph)
        draw_rounded_rect(self.screen, (10, 40, 10), box, radius=16,
                          border=3, border_colour=GREEN)

        mouse = pygame.mouse.get_pos()

        t = self.font_xl.render("YOU WIN! 🎉", True, YELLOW)
        self.screen.blit(t, (px + pw // 2 - t.get_width() // 2, py + 16))

        # Show new highscore badge
        if self.new_hs:
            hs_surf = self.font_md.render("★ NEW HIGHSCORE! ★", True, GOLD)
            self.screen.blit(hs_surf,
                (px + pw // 2 - hs_surf.get_width() // 2, py + 82))

        m  = int(self.elapsed_final // 60)
        s  = int(self.elapsed_final % 60)
        ms = int((self.elapsed_final * 1000) % 1000)
        time_str = self.font_sm.render(
            f"Time: {m:02}:{s:02}:{ms:03}   Hits: {self.player.collisions}",
            True, WHITE
        )
        self.screen.blit(time_str,
            (px + pw // 2 - time_str.get_width() // 2, py + 120))

        bw, bh = 130, 40
        gap = (pw - bw * 3 - 20) // 2
        y_btn = py + ph - 66

        self._popup_restart   = pygame.Rect(px + 14,           y_btn, bw, bh)
        self._popup_scores    = pygame.Rect(px + 14 + bw + gap, y_btn, bw, bh)
        self._popup_quit      = pygame.Rect(px + pw - bw - 14,  y_btn, bw, bh)

        make_button(self.screen, "Play Again",  self._popup_restart, self.font_sm,
                    mouse_pos=mouse)
        make_button(self.screen, "Highscores",  self._popup_scores,  self.font_sm,
                    bg=(60, 100, 40), hover_bg=(90, 150, 60), mouse_pos=mouse)
        make_button(self.screen, "Main Menu",   self._popup_quit,    self.font_sm,
                    bg=(100, 40, 40), hover_bg=(160, 60, 60), mouse_pos=mouse)

    def draw(self):
        self.screen.fill(BLACK)
        off_y = self._offset_y()

        self._draw_maze(off_y)
        self._draw_goal(off_y)
        self._draw_player(off_y)
        self._draw_panel()

        if self.game_over:
            self._draw_gameover_popup()
        elif self.game_won:
            self._draw_win_popup()

        pygame.display.flip()

    # ── update ───────────────────────────────────────────

    def update(self):
        # Check game-over (too many collisions)
        if not self.game_over and not self.game_won:
            if self.player.collisions > MAX_COLLISIONS:
                self.game_over = True
                self.elapsed_final = time.time() - self.start_time

        # Check win
        if (
            not self.game_won
            and not self.game_over
            and self.player.x == self.goal_x
            and self.player.y == self.goal_y
        ):
            self.game_won      = True
            self.elapsed_final = time.time() - self.start_time
            self.new_hs        = is_new_highscore(self.difficulty, self.elapsed_final)
            save_score(
                self.difficulty,
                self.player_name,
                self.elapsed_final,
                self.player.collisions,
            )
            if sounds.victory_sound:
                sounds.victory_sound.play()

    # ── main loop ────────────────────────────────────────

    def run(self):
        """Run the game loop. Returns 'menu' or 'quit'."""
        self._popup_restart = None
        self._popup_quit    = None
        self._popup_scores  = None
        self._btn_restart   = None
        self._btn_menu      = None
        self._btn_hs        = None

        while True:
            self.clock.tick(FPS)
            mouse = pygame.mouse.get_pos()

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit

                # ── mouse clicks ─────────────────────────
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                    # Panel buttons (always active)
                    if self._btn_restart and self._btn_restart.collidepoint(mouse):
                        self.new_game()
                        continue
                    if self._btn_menu and self._btn_menu.collidepoint(mouse):
                        return "menu"
                    if self._btn_hs and self._btn_hs.collidepoint(mouse):
                        result = show_highscore_screen(
                            self.screen, self.difficulty, self.clock
                        )
                        if result == "menu":
                            return "menu"
                        self.new_game()
                        continue

                    # Popup buttons
                    if self.game_over:
                        if self._popup_restart and self._popup_restart.collidepoint(mouse):
                            self.new_game()
                        elif self._popup_quit and self._popup_quit.collidepoint(mouse):
                            return "menu"

                    elif self.game_won:
                        if self._popup_restart and self._popup_restart.collidepoint(mouse):
                            self.new_game()
                        elif self._popup_quit and self._popup_quit.collidepoint(mouse):
                            return "menu"
                        elif self._popup_scores and self._popup_scores.collidepoint(mouse):
                            result = show_highscore_screen(
                                self.screen, self.difficulty, self.clock
                            )
                            if result == "menu":
                                return "menu"
                            self.new_game()

                # ── keyboard ─────────────────────────────
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.new_game()
                        continue
                    if event.key == pygame.K_q:
                        return "menu"
                    if event.key == pygame.K_h:
                        result = show_highscore_screen(
                            self.screen, self.difficulty, self.clock
                        )
                        if result == "menu":
                            return "menu"
                        self.new_game()
                        continue

                    # Movement — only when playing
                    if self.game_won or self.game_over:
                        continue

                    moved = False
                    if event.key == pygame.K_UP:
                        moved = self.player.move(0, -1, self.grid)
                    elif event.key == pygame.K_DOWN:
                        moved = self.player.move(0,  1, self.grid)
                    elif event.key == pygame.K_LEFT:
                        moved = self.player.move(-1, 0, self.grid)
                    elif event.key == pygame.K_RIGHT:
                        moved = self.player.move( 1, 0, self.grid)

                    if not moved and sounds.collision_sound:
                        sounds.collision_sound.play()

            self.update()
            self.draw()