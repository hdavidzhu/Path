"""
Path - The Journey of Bob
By: David Zhu and Charlie Mouton
"""
import sys, pygame, pygame.mixer, copy
from copy import deepcopy as dcp
from pygame.locals import *

# Define colors.
black = 0,0,0
white = 255,255,255
red = 255,0,0   # This is the side reference for creating the whole game grid.
playercolor = 255,56,25
nodecolor = 217,217,217
wallcolor = 130,130,130
lavacolor = 217,15,0
icecolor = 94,227,255
mudcolor = 127,87,52
reversecolor = 145,33,196
startcolor = 255,235,62
endcolor = 63,255,62

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
        self.choice = None

        # Create base nodes.
        for x in range(0,swidth,ref):
            for y in range(0,sheight,ref):
                node = Node(self,x,y)
                self.world[(node.x,node.y)] = node
        
        # Create Outer boundaries.
        for x in range(0,swidth,ref):
            for y in range(0,sheight,ref):
                if x not in range(3*ref,swidth-3*ref,ref) or y not in range(3*ref,sheight-3*ref,ref):
                    boundary = Wall(self,x,y)
                    boundary.color = black
                    self.world[(boundary.x,boundary.y)] = boundary

        # Create block palette.
        world[(2*ref,ref)] = Wall(self,2*ref,ref)
        world[(4*ref,ref)] = Lava(self,4*ref,ref)
        world[(6*ref,ref)] = Ice(self,6*ref,ref)
        world[(8*ref,ref)] = Mud(self,8*ref,ref)
        world[(10*ref,ref)] = Reverse(self,10*ref,ref)
        world[(12*ref,ref)] = Start(self,12*ref,ref)
        world[(14*ref,ref)] = End(self,14*ref,ref)


    def getitem(self,x,y):
        return world[(x,y)]

    def placeitem(self, choice, x, y):
        if x in range(3*ref,swidth-3*ref,ref) and y in range(3*ref,sheight-3*ref,ref):
            if str(choice.__class__) == '__main__.Start':
                for block in world:
                    if str(world[block].__class__) == '__main__.Start':
                        if block[1] == ref:
                            pass
                        else:
                            world[block] = Node(model,block[0],block[1])
            if self.world[(x,y)].__class__ == choice.__class__:
                pass
            else:
                block = choice.__class__(model,x,y)
                self.world[(block.x,block.y)] = block

    def update(self):
        return self.player.update()

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
        self.right = self.x + self.side
        self.top = self.y
        self.bottom = self.y + self.side
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

        return local_area

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
        self.right = self.x + self.side
        self.top = self.y
        self.bottom = self.y + self.side

class Node(Block):
    """A node is a floor block of our character."""
    def __init__(self, model, x, y):
        Block.__init__(self, nodecolor, x, y)
        self.player = model.player

    def interact(self,player):
        if abs(self.player.vx) <= self.player.maxspeed:
            self.player.x += self.player.vx
        else:
            self.player.vx = self.player.vx/abs(self.player.vx)*self.player.maxspeed
            self.player.x += self.player.vx
        if abs(self.player.vy) <= self.player.maxspeed:
            self.player.y += self.player.vy
        else:
            self.player.vy = self.player.vy/abs(self.player.vy)*self.player.maxspeed
            self.player.y += self.player.vy

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
        self.player = model.player

    def interact(self,player):
        return 'lava'

class Ice(Block, Node):
    def __init__(self, model, x, y):
        Block.__init__(self, icecolor, x, y)
        self.player = model.player
        
class Mud(Block):
    def __init__(self, model, x, y):
        Block.__init__(self, mudcolor, x, y)
        self.player = model.player

    def interact(self,player):
        return 'mud'

class Reverse(Block, Node):
    def __init__(self,model,x,y):
        Block.__init__(self, reversecolor, x, y)
        self.player = model.player    

class Start(Block, Node):
    def __init__(self, model, x, y):
        Block.__init__(self, startcolor, x, y)
        self.player = model.player

class End(Block):
    def __init__(self, model, x, y):
        Block.__init__(self, endcolor, x, y)
        self.model = model

    def interact(self,player):
        return 'end'

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
        local_area = model.update()
        state = 'node'

        for block in local_area:
            if str(block.__class__) == '__main__.Ice':
                return
            if str(block.__class__) == '__main__.Reverse':
                state = 'reverse'

        if state == 'node':
            if event.key == pygame.K_LEFT:
                self.model.player.vx += -self.speed
            if event.key == pygame.K_RIGHT:
                self.model.player.vx += self.speed
            if event.key == pygame.K_UP:
                self.model.player.vy += -self.speed
            if event.key == pygame.K_DOWN:
                self.model.player.vy += self.speed
        elif state == 'reverse':
            if event.key == pygame.K_LEFT:
                self.model.player.vx += self.speed
            if event.key == pygame.K_RIGHT:
                self.model.player.vx += -self.speed
            if event.key == pygame.K_UP:
                self.model.player.vy += self.speed
            if event.key == pygame.K_DOWN:
                self.model.player.vy += -self.speed

        if event.key == pygame.K_ESCAPE:
            self.model.choice = None
        if event.key == pygame.K_r:
            for block in self.model.world:
                if str(self.model.world[block].__class__) == '__main__.Start':
                    if block[1] == ref:
                        pass
                    else:
                        self.model.player.x = block[0]
                        self.model.player.y = block[1]
                        self.model.player.vx = 0
                        self.model.player.vy = 0
                else:
                    pass

    def handle_mouse_event(self, event):
        if event.type != MOUSEBUTTONDOWN:
            return
        if event.type == MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            mx, my = roundpoint(mx, my)
            if self.model.choice == None:
                self.model.choice = model.getitem(mx, my)
            else:
                model.placeitem(self.model.choice,mx,my)


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