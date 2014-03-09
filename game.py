"""
Path - The Journey of Bob
By: David Zhu and Charlie Mouton
"""
import sys, pygame, pygame.mixer
from pygame.locals import *

# Define colors.
black = 0,0,0
white = 255,255,255
red = 255,0,0   # This is the side reference for creating the whole game grid.
wallcolor = 130,130,130
nodecolor = 217,217,217
playercolor = 255,56,25
lavacolor = 217,15,0
reversecolor = 145,33,196

# Global declaration of the world which the player interacts with.
world = {}

# Set screen sizes and declare ref for future reference for blocks.
global ref
global swidth
global sheight
ref = 20
swidth = 36*ref
sheight = 24*ref

def roundpoint(a, b):
    """
    Floors input point into the nearest upper left grid point.

    a: x coordinate
    b: y coordinate
    """
    return ((int(a) / ref) * ref, (int(b) / ref) * ref)

class PathModel:
    """Encodes game state."""
    def __init__(self):
        self.player = Player((255,255,255),.75*ref,100,370)
        self.world = world
        for x in range(0,swidth,ref):
            for y in range(0,sheight,ref):
                node = Node(self,x,y)
                self.world[(node.x,node.y)] = node
        for x in range(0,swidth,ref):
            for y in range(0,sheight,ref):
                if x not in range(ref,swidth-ref,ref) or y not in range(ref,sheight-ref,ref):
                    boundary = Wall(self,x,y)
                    self.world[(boundary.x,boundary.y)] = boundary

    def placeitem(self, x, y):
        wall = Wall(self,x,y)
        self.world[(wall.x,wall.y)] = wall

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
        self.left = self.x
        self.right = x + self.side
        self.top = self.y
        self.bottom = y + self.side
        self.vx = 0.0
        self.vy = 0.0
        self.maxspeed = 1.0

    def update(self):
        """Updates boundaries."""
        self.left = self.x
        self.right = self.x + self.side
        self.top = self.y
        self.bottom = self.y + self.side

        # Interaction - checks collisions of player with the world.
        ul = roundpoint(self.left, self.top)
        ur = roundpoint(self.right, self.top)
        ll = roundpoint(self.left, self.bottom)
        lr = roundpoint(self.right, self.bottom)

        # Find the local area for the character.
        local_area = [world[ul],world[ur],world[ll],world[lr]]

        # Analyze for each area.
        for block in local_area:
            block.interact(self)

class Block():
    """
    Creates a block for the game. Currently it inherits from pygame sprite because of pygame's inherent edge detection code.
    """
    def __init__(self, color, x, y):
        self.color = color
        self.side = ref
        self.x = x
        self.y = y
        self.left = self.x
        self.right = x + self.side
        self.top = self.y
        self.bottom = y + self.side

class Node(Block):
    """A node is a floor block of our character."""
    def __init__(self, model, x, y):
        Block.__init__(self, nodecolor, x, y)
        self.model = model

    def interact(self,player):
        if abs(self.model.player.vx) <= self.model.player.maxspeed:
            self.model.player.x += self.model.player.vx
        else:
            self.model.player.vx = self.model.player.vx/abs(self.model.player.vx)*self.model.player.maxspeed
            self.model.player.x += self.model.player.vx
        if abs(self.model.player.vy) <= self.model.player.maxspeed:
            self.model.player.y += self.model.player.vy
        else:
            self.model.player.vy = self.model.player.vy/abs(self.model.player.vy)*self.model.player.maxspeed
            self.model.player.y += self.model.player.vy

class Wall(Block):
    def __init__(self, model, x, y):
        Block.__init__(self, wallcolor, x, y)

    def interact(self,player):
        comparisons = [abs(player.left - self.right), abs(player.right - self.left), abs(player.bottom - self.top), abs(player.top - self.bottom)]
        choice = comparisons.index(min(comparisons))
        if choice == 0:
            player.x += comparisons[choice]
            player.vx = 0.0
        elif choice == 1:
            player.x -= comparisons[choice]
            player.vx = 0.0
        elif choice == 2:
            player.y -= comparisons[choice]
            player.vy = 0.0
        elif choice == 3:
            player.y += comparisons[choice]
            player.vy = 0.0
        else:
            print "ERROR."

class Lava(Block):
    def __init__(self, model, x, y):
        Block.__init__(self, lavacolor, x, y)
        self.model = model

    # def interact(self, player):
    #     Node.interact(self, player)

class Start(Block):
    pass

class End(Block):
    pass

class Ice(Block):
    pass

class Mud(Block):
    pass

class Reverse(Block):
    def __init__(self,model,x,y):
        Block.__init__(self, reversecolor, x, y)
        self.model = model       

    pass

class PyGamePathView:
    """
    Game viewer in pygame window.
    """
    def __init__(self,model,screen):
        self.model = model
        self.screen = screen

    def draw(self):
        self.screen.fill(pygame.Color(black[0],black[1],black[2]))
        
        for block in self.model.world:
            value = self.model.world[block]
            temp = pygame.Rect(value.x,value.y,value.side,value.side)
            pygame.draw.rect(self.screen, pygame.Color(value.color[0],value.color[1],value.color[2]),temp)

        # Draws player.
        temp = pygame.Rect(self.model.player.x,self.model.player.y,self.model.player.side,self.model.player.side)
        pygame.draw.rect(self.screen, pygame.Color(playercolor[0],playercolor[1],playercolor[2]),temp)

        pygame.display.update()

        # Keep time constant.
        clock.tick(60)

class PyGamePathController:
    """
    Handles keyboard inputs.
    """
    def __init__(self,model,speed):
        self.model = model
        self.speed = speed

    def handle_keyboard_event(self, event):
        if event.key == pygame.K_LEFT:
            self.model.player.vx += -self.speed
        if event.key == pygame.K_RIGHT:
            self.model.player.vx += self.speed
        if event.key == pygame.K_UP:
            self.model.player.vy += -self.speed
        if event.key == pygame.K_DOWN:
            self.model.player.vy += self.speed

    def handle_mouse_event(self, event):
        if event.type != MOUSEBUTTONDOWN:
            return
        if event.type == MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            mx, my = roundpoint(mx, my)
            model.placeitem(mx,my)

if __name__ == '__main__':
    pygame.init()

    size = swidth, sheight

    screen = pygame.display.set_mode(size)
    clock = pygame.time.Clock()
    speed = .25

    model = PathModel()
    view = PyGamePathView(model, screen)
    controller = PyGamePathController(model,speed)

    running = True

    while running:
        # Checks for any type of user input.
        for event in pygame.event.get():
            # Exits script when exit button is pressed.
            if event.type == QUIT:
                running = False
            if event.type == KEYDOWN:
                controller.handle_keyboard_event(event)
            if event.type == MOUSEBUTTONDOWN:
                controller.handle_mouse_event(event)
        model.update()
        view.draw()
        clock.tick(60)
        
    pygame.quit()