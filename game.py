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
wallcolor = 130, 130,130
nodecolor = 217, 217, 217
playercolor = 111, 255, 137

# Set screen sizes and declare ref for future reference for blocks.
global ref
global swidth
global sheight
ref = 20
swidth = 36*ref
sheight = 24*ref

class PathModel:
    """
    Encodes game state.
    """
    def __init__(self):
        self.player = Player((255,255,255),10,10,370)
        self.nodes = []
        for x in range(0,swidth,ref):
            for y in range(0,sheight,ref):
                node = Node(x,y)
                self.nodes.append(node)
        self.boundaries = []
        for x in range(0,swidth,ref):
            for y in range(0,sheight,ref):
                if x not in range(ref,swidth-ref,ref) or y not in range(ref,sheight-ref,ref):
                    boundary = Wall(x,y)
                    self.boundaries.append(boundary)


    def update(self):
        self.player.update()

class Player():
    """
    Creates a player for the game. Currently it inherits from pygame sprite because of pygame's inherent edge detection code.
    """
    def __init__(self, color, side, x, y):
        self.color = color
        self.side = side
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
    def __init__(self, color, x, y):
        self.color = color
        self.side = ref
        self.x = x
        self.y = y

class Node(Block):
    def __init__(self, x, y):
        Block.__init__(self, black, x, y)

class Wall(Block):
    def __init__(self, x, y):
        Block.__init__(self, wallcolor, x, y)

class PyGamePathView:
    """
    Game viewer in pygame window.
    """
    def __init__(self,model,screen):
        self.model = model
        self.screen = screen

    def draw(self):
        self.screen.fill(pygame.Color(red[0],red[1],red[2]))
        
        # Draws nodes.
        for node in self.model.nodes:
            temp = pygame.Rect(node.x,node.y,node.side,node.side)
            pygame.draw.rect(self.screen, pygame.Color(nodecolor[0],nodecolor[1],nodecolor[2]),temp)

        # Draws outer boundaries.
        for boundary in self.model.boundaries:
            temp = pygame.Rect(boundary.x,boundary.y,boundary.side,boundary.side)
            pygame.draw.rect(self.screen, pygame.Color(wallcolor[0],wallcolor[1],wallcolor[2]),temp)

        # Draws player.
        temp = pygame.Rect(self.model.player.x,self.model.player.y,self.model.player.side,self.model.player.side)
        pygame.draw.rect(self.screen, pygame.Color(playercolor[0],playercolor[1],playercolor[2]),temp)
        
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

    size = swidth, sheight

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
