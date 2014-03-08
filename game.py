import sys, pygame, pygame.mixer
from pygame.locals import *

pygame.init()

clock = pygame.time.Clock()
size = width, height = 600, 400
screen = pygame.display.set_mode(size)
black = 0,0,0

class PathModel:
    pass

class Bob:
    pass

class Blocks:
    pass

class PathBuildView:
    pass

class PathPlayView:
    pass

class PathKeyboardController:
    pass

class PathMouseController:
    pass


while True:
    # Checks for any type of user input.
    for event in pygame.event.get():
        # Exits script when exit button is pressed.
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == KEYDOWN and event.key == K_ESCAPE:
            sys.exit()

    # Fill background with black to wipe any pre-existing states.
    screen.fill(black)

    # Keep the game pace stable.
    clock.tick(60)
