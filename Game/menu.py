import pygame
from settings import *
from leaderboard import get_scores


def draw_rounded_rect(surface, colour, rect, radius=12, border=0, border_colour=None):
    pygame.draw.rect(surface, colour, rect, border_radius=radius)
    if border and border_colour:
        pygame.draw.rect(surface, border_colour, rect, border, border_radius=radius)


def make_button(surface, text, rect, font,
                bg=(60, 60, 120), fg=WHITE,
                hover_bg=(90, 90, 180), border_colour=PANEL_BORDER,
                mouse_pos=None):
    hovered = rect.collidepoint(mouse_pos) if mouse_pos else False
    colour = hover_bg if hovered else bg
    draw_rounded_rect(surface, colour, rect, radius=10, border=2, border_colour=border_colour)
    label = font.render(text, True, fg)
    lx = rect.centerx - label.get_width() // 2
    ly = rect.centery - label.get_height() // 2
    surface.blit(label, (lx, ly))
    return hovered


class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.clock  = pygame.time.Clock()

        self.font_title  = pygame.font.SysFont(None, 72)
        self.font_sub    = pygame.font.SysFont(None, 34)
        self.font_btn    = pygame.font.SysFont(None, 30)
        self.font_small  = pygame.font.SysFont(None, 24)

        self.player_name = ""
        self.difficulty  = "easy"
        self.input_active = True

        W, H = screen.get_size()

        # Name input box
        self.input_rect = pygame.Rect(W // 2 - 140, 210, 280, 44)

        # Difficulty buttons
        diff_y   = 310
        bw, bh   = 110, 40
        spacing  = 18
        total_w  = bw * 3 + spacing * 2
        start_x  = W // 2 - total_w // 2
        self.diff_rects = {
            "easy":   pygame.Rect(start_x,              diff_y, bw, bh),
            "medium": pygame.Rect(start_x + bw + spacing, diff_y, bw, bh),
            "hard":   pygame.Rect(start_x + (bw + spacing) * 2, diff_y, bw, bh),
        }

        # Play button
        self.play_rect = pygame.Rect(W // 2 - 100, 380, 200, 48)

        # Highscores button
        self.hs_rect   = pygame.Rect(W // 2 - 100, 440, 200, 40)

    def run(self):
        """Returns (player_name, difficulty) when Play is pressed, or raises SystemExit."""
        while True:
            mouse = pygame.mouse.get_pos()
            W, H  = self.screen.get_size()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.input_rect.collidepoint(mouse):
                        self.input_active = True
                    else:
                        self.input_active = False

                    for diff, rect in self.diff_rects.items():
                        if rect.collidepoint(mouse):
                            self.difficulty = diff

                    if self.play_rect.collidepoint(mouse) and self.player_name.strip():
                        return self.player_name.strip(), self.difficulty

                    if self.hs_rect.collidepoint(mouse):
                        self._show_scores()

                if event.type == pygame.KEYDOWN:
                    if self.input_active:
                        if event.key == pygame.K_BACKSPACE:
                            self.player_name = self.player_name[:-1]
                        elif event.key == pygame.K_RETURN:
                            if self.player_name.strip():
                                return self.player_name.strip(), self.difficulty
                        elif len(self.player_name) < 16:
                            if event.unicode.isprintable():
                                self.player_name += event.unicode

            self._draw(mouse)
            self.clock.tick(60)

    def _draw(self, mouse):
        W, H = self.screen.get_size()
        self.screen.fill((15, 15, 30))

        # Title
        title = self.font_title.render("2D MAZE", True, GOLD)
        self.screen.blit(title, (W // 2 - title.get_width() // 2, 60))
        sub = self.font_sub.render("Can you find your way out?", True, GRAY)
        self.screen.blit(sub, (W // 2 - sub.get_width() // 2, 138))

        # Name label + input
        lbl = self.font_btn.render("Enter your name:", True, WHITE)
        self.screen.blit(lbl, (W // 2 - lbl.get_width() // 2, 182))
        border_col = GOLD if self.input_active else PANEL_BORDER
        draw_rounded_rect(self.screen, (30, 30, 60), self.input_rect,
                          radius=8, border=2, border_colour=border_col)
        name_surf = self.font_btn.render(self.player_name + ("|" if self.input_active else ""),
                                         True, WHITE)
        self.screen.blit(name_surf,
            (self.input_rect.x + 10, self.input_rect.centery - name_surf.get_height() // 2))

        # Difficulty label
        dl = self.font_btn.render("Select difficulty:", True, WHITE)
        self.screen.blit(dl, (W // 2 - dl.get_width() // 2, 278))

        diff_colours = {
            "easy":   ((30, 110, 30),  (50, 170, 50)),
            "medium": ((110, 80, 0),   (180, 130, 0)),
            "hard":   ((110, 20, 20),  (180, 40, 40)),
        }
        for diff, rect in self.diff_rects.items():
            bg, hov = diff_colours[diff]
            selected = self.difficulty == diff
            bord = GOLD if selected else PANEL_BORDER
            fg   = GOLD if selected else WHITE
            make_button(self.screen, diff.capitalize(), rect, self.font_btn,
                        bg=bg, hover_bg=hov, fg=fg, border_colour=bord, mouse_pos=mouse)

        # Play button
        can_play = bool(self.player_name.strip())
        pb = (40, 120, 40) if can_play else (50, 50, 50)
        ph = (60, 180, 60) if can_play else (50, 50, 50)
        make_button(self.screen, "▶  Play", self.play_rect, self.font_sub,
                    bg=pb, hover_bg=ph, mouse_pos=mouse if can_play else None)
        if not can_play:
            hint = self.font_small.render("Type your name to play", True, GRAY)
            self.screen.blit(hint, (W // 2 - hint.get_width() // 2, 435))

        # Highscores
        make_button(self.screen, "🏆  Highscores", self.hs_rect, self.font_btn,
                    bg=(60, 100, 40), hover_bg=(90, 150, 60), mouse_pos=mouse)

        pygame.display.flip()

    def _show_scores(self):
        from game import show_highscore_screen
        show_highscore_screen(self.screen, self.difficulty, self.clock)