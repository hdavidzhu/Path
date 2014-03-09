"""
Path - The Journey of Bob
By: David Zhu and Charlie Mouton
"""

import sys, pygame, pygame.mixer
from pygame.locals import *

# Define colors.
black = 0,0,0
white = 255,255,255
red = 255,0,0

class PathModel:
    """
    Encodes game state.
    """
    def __init__(self):
        self.player = Player((255,255,255),10,10,370)

    def update(self):
        self.player.update()
    pass

class Player():
    """
    Creates a player for the game. Currently it inherits from pygame sprite because of pygame's inherent edge detection code.
    """
    def __init__(self, color, side, x, y):
        self.color = color
        self.height = side
        self.width = side
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.maxx = 2.0
        self.maxy = 2.0

    def update(self):
        if abs(self.vx) <= self.maxx:
            self.x += self.vx
        else:
            self.vx = self.vx/abs(self.vx)*self.maxx
            self.x += self.vx
        if abs(self.vy) <= self.maxy:
            self.y += self.vy
        else:
            self.vy = self.vy/abs(self.vy)*self.maxy
            self.y += self.vy
    pass

class Block():
    """
    Creates a block for the game. Currently it inherits from pygame sprite because of pygame's inherent edge detection code.
    """
    def __init__(self, color, height, width, x, y):
        self.color = color
        self.height = height
        self.width = width
        self.x = x
        self.y = y
    pass

class PyGamePathView:
    """
    Game viewer in pygame window.
    """
    def __init__(self,model,screen):
        self.model = model
        self.screen = screen

    def draw(self):
        self.screen.fill(pygame.Color(red[0],red[1],red[2]))
        rect = pygame.Rect(self.model.player.x,self.model.player.y,self.model.player.width,self.model.player.height)
        pygame.draw.rect(self.screen, pygame.Color(white[0],white[1],white[2]),rect)
        pygame.display.update()


        # Keep time constant.
        clock.tick(60)
    pass

class PyGamePathKeyboardController:
    """
    Handles keyboard inputs.
    """
    def __init__(self,model,speed):
        self.model = model
        self.speed = speed

    def handle_keyboard_event(self, event):
        if event.type != KEYDOWN:
            return
        if event.key == pygame.K_LEFT:
            self.model.player.vx += -self.speed
        if event.key == pygame.K_RIGHT:
            self.model.player.vx += self.speed
        if event.key == pygame.K_UP:
            self.model.player.vy += -self.speed
        if event.key == pygame.K_DOWN:
            self.model.player.vy += self.speed
    pass

class PathMouseController:
    pass

if __name__ == '__main__':
    pygame.init()

    size = width, height = 600, 400
    screen = pygame.display.set_mode(size)
    clock = pygame.time.Clock()
    speed = .5

    model = PathModel()
    view = PyGamePathView(model, screen)
    controller = PyGamePathKeyboardController(model,speed)

    running = True

    while running:
        # Checks for any type of user input.
        for event in pygame.event.get():
            # Exits script when exit button is pressed.
            if event.type == QUIT:
                running = False
            if event.type == KEYDOWN:
                controller.handle_keyboard_event(event)
        model.update()
        view.draw()
        clock.tick(60)
        
    pygame.quit()
