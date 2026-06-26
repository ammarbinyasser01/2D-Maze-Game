import pygame
from menu import Menu
from game import Game


def main():
    pygame.init()
    pygame.mixer.pre_init(44100, -16, 1, 512)
    pygame.mixer.init()
    print(f"[main] mixer: {pygame.mixer.get_init()}")

    # Load sounds AFTER mixer is confirmed running
    from sounds import load_sounds
    load_sounds()

    screen = pygame.display.set_mode((700, 600))
    pygame.display.set_caption("2D Maze Game")

    while True:
        menu = Menu(screen)
        player_name, difficulty = menu.run()

        game = Game(screen, player_name, difficulty)
        result = game.run()

        screen = pygame.display.get_surface()

        if result != "menu":
            break


if __name__ == "__main__":
    main()