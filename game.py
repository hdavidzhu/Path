import sys, pygame, pygame.mixer
from pygame.locals import *

from pygame.init()

clock = pygame.time.clock()
size = width, height = 600, 400
black = 0,0,0

while True:
    # Checks for any type of user input.
    for event in pygame.events.get():
        pass

    # Fill background with black to wipe any pre-existing states.
    screen.fill(black)

    # Keep the game pace stable.
    clock.tick(60)
