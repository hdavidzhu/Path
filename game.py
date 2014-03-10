"""
Path - The Journey of Bob
By: David Zhu and Charlie Mouton
"""
import sys, pygame, pygame.mixer, copy, easygui
from copy import deepcopy as dcp
from time import time
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
playbuildcolor = 0,0,0

# Set screen sizes and declare ref for future reference for blocks.
ref = 20
swidth = 36*ref
sheight = 24*ref

# Buttons

playbutton = pygame.image.load('play.jpg')
playbutton = pygame.transform.scale(playbutton, (ref,ref))

pausebutton = pygame.image.load('pause.png')
pausebutton = pygame.transform.scale(pausebutton, (ref,ref))

saveimage = pygame.image.load('save.png')
saveimage = pygame.transform.scale(saveimage,(ref,ref))

loadimage = pygame.image.load('load.png')
loadimage = pygame.transform.scale(loadimage, (ref,ref))

bob = pygame.image.load('bob.png')
bob = pygame.transform.scale(bob, (15,15))

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
        self.player = Player(self,(255,255,255),.75*ref,100,370)
        self.world = {}
        self.palette = {}
        self.playmode = False
        self.endmode = False
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
        self.palette[(3*ref,ref)] = self.world[(3*ref,ref)] = Wall(self,3*ref,ref)
        self.palette[(5*ref,ref)] = self.world[(5*ref,ref)] = Lava(self,5*ref,ref)
        self.palette[(7*ref,ref)] = self.world[(7*ref,ref)] = Ice(self,7*ref,ref)
        self.palette[(9*ref,ref)] = self.world[(9*ref,ref)] = Mud(self,9*ref,ref)
        self.palette[(11*ref,ref)] = self.world[(11*ref,ref)] = Reverse(self,11*ref,ref)
        self.palette[(13*ref,ref)] = self.world[(13*ref,ref)] = Start(self,13*ref,ref)
        self.palette[(15*ref,ref)] = self.world[(15*ref,ref)] = End(self,15*ref,ref)

        # Create playbuild button.
        self.playbuild = PlayBuild(self,ref,ref)

        # Create save button.
        self.savebutton = None

        # Create load button.
        self.loadbutton = Load(self,ref,5*ref)

    def getitem(self,x,y):
        """
        Upon mouseclick, we capture the type of block that is selected and adds it to be prepared to be placed upon second and subsequent mouseclicks.
        """
        return self.world[(x,y)]

    def placeitem(self, choice, x, y):
        """
        This takes a stored type of block and places in the selected grid square.

        choice: the stored block type.
        """
        if x in range(3*ref,swidth-3*ref,ref) and y in range(3*ref,sheight-3*ref,ref):
            if str(choice.__class__) == '__main__.Start':
                for block in self.world:
                    if str(self.world[block].__class__) == '__main__.Start':
                        if block[1] == ref:
                            pass
                        else:
                            self.world[block] = Node(model,block[0],block[1])
            if self.world[(x,y)].__class__ == choice.__class__:
                pass
            else:
                block = choice.__class__(model,x,y)
                self.world[(block.x,block.y)] = block

    def update(self):
        return self.player.update()

    def save(self):
            input_msg = easygui.enterbox(msg='Enter the name of your level (*.txt). No spaces, please.', title='Hello!', default='', strip=True)
            if input_msg:
                # Grabs game window state.
                temp = {}
                for block in self.world:
                    if block[0] in range(3*ref,swidth-3*ref,ref) and block[1] in range(3*ref,sheight-3*ref,ref):
                        temp[block] = str(self.world[block].__class__)
                target = open(input_msg+'.txt','a')
                target.write(str(temp))

    def load(self):
        for block in self.world:
            if block[0] in range(3*ref,swidth-3*ref,ref) and block[1] in range(3*ref,sheight-3*ref,ref):
                self.world[block] = Node(self,block[0],block[1])

        temp = easygui.enterbox(msg='What level do you want to play?', title='Load', default='', strip=True)
        if temp:
            target = open(temp,'r')
            temp = eval(target.read())
            for thing in temp:
                for block in self.palette:                
                    if str(self.palette[block].__class__) == temp[thing]:
                        self.world[thing] = self.palette[block].__class__(self,thing[0],thing[1])

class Player():
    """
    Creates a player for the game. Currently it inherits from pygame sprite because of pygame's inherent edge detection code.
    """
    def __init__(self, model, color, side, x, y):
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
        local_area = [model.world[ul],model.world[ur],model.world[ll],model.world[lr]]

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
        """
        The interaction for Node is typical motion. it moves in x and y by an increment of vx and vy.
        """
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
    """ A basic wall structure that stops the character."""
    def __init__(self, model, x, y):
        Block.__init__(self, wallcolor, x, y)

    def interact(self,player):
        """
        This is the meat of our collision detection code. We assume that in one time step, our character finds himself within a wall block. We look at the 
        relative differences between each side of our character and the corresponding wall sides. We then find the smallest difference and reset the position
        of the character back that distance in that direction, using if statements to determine the direction that our character was moving. We then set the 
        velocity in that direction to 0.
        """
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
    """ A lava block spells instant death for our character if any part of him touches it."""
    def __init__(self, model, x, y):
        Block.__init__(self, lavacolor, x, y)
        self.player = model.player

    def interact(self,player):
        """The lava block kills our character, thus returning his position to the starting block."""
        for block in model.world:
            if str(model.world[block].__class__) == '__main__.Start' and block[1] != ref:
                self.player.x = block[0] + .125*ref
                self.player.y = block[1] + .125*ref
                self.player.vx = 0
                self.player.vy = 0
        
class Ice(Block, Node):
    """ 
    This block disallows our character from changing its velocity. Can spell doom for our character if a wall kills its velocity while on ice.
    To do this, we have our controller look at what blocks are near our character and in the case of them is ice, it nulls the affects of any movement
    inputs. However, the internal interaction of our character is the same as Node (having x and y change depending on vx and vy), so we inherit Node's 
    interact method.
    """
    def __init__(self, model, x, y):
        Block.__init__(self, icecolor, x, y)
        self.player = model.player
        
class Mud(Block):
    """This block causes our character's max velocity to drop dramatically."""
    def __init__(self, model, x, y):
        Block.__init__(self, mudcolor, x, y)
        self.player = model.player

    def interact(self,player):
        if abs(self.player.vx) <= self.player.maxspeed/4:
            self.player.x += self.player.vx
        else:
            self.player.vx = self.player.vx/abs(self.player.vx)*self.player.maxspeed/4
            self.player.x += self.player.vx
        if abs(self.player.vy) <= self.player.maxspeed/4:
            self.player.y += self.player.vy
        else:
            self.player.vy = self.player.vy/abs(self.player.vy)*self.player.maxspeed/4
            self.player.y += self.player.vy
        

class Reverse(Block, Node):
    """
    This block reverses the controls for our character. To do this, we have our controller look at what blocks are near our character, and in the case one 
    of them is reverse, it reverses what the input buttons do.
    """
    def __init__(self,model,x,y):
        Block.__init__(self, reversecolor, x, y)
        self.player = model.player    

class Start(Block, Node):
    """ 
    This block marks where the character teleports to in the case of death or a key press restart.
    The interact for this block is the same as Node, so we inherit Node for this class.
    """
    def __init__(self, model, x, y):
        Block.__init__(self, startcolor, x, y)
        self.player = model.player

class End(Block):
    """
    This block marks the end of the level. When the character reaches this block, options become available to save the level for future use.
    """
    def __init__(self, model, x, y):
        Block.__init__(self, endcolor, x, y)
        self.model = model

    def interact(self,player):
        """"""
        for block in model.world:
            if str(model.world[block].__class__) == '__main__.Start' and block[1] != ref:
                model.player.x = block[0] + .125*ref
                model.player.y = block[1] + .125*ref
                model.player.vx = 0
                model.player.vy = 0

        # Create save button.
        # choices = ['Yes', 'No']
        # reply = easygui.buttonbox(msg="Congrats! You've beat your level. Would you like to save?", title='Well Done!', choices=choices)
        # if reply == "Yes":
        #     model.save()
        self.model.savebutton = Save(self,ref,3*ref)
        self.model.endmode = True
        self.model.playmode = False



class PlayBuild(Block):
    def __init__(self, model, x, y):
        Block.__init__(self, black, x, y)

class Save(Block):
    def __init__(self, model, x, y):
        Block.__init__(self, black, x, y)

class Load(Block):
    def __init__(self, model, x, y):
        Block.__init__(self, black, x, y)


class PyGamePathView:
    """
    Game viewer in pygame window.
    """
    def __init__(self,model,screen):
        self.model = model
        self.screen = screen

    def draw(self):
        self.screen.fill(pygame.Color(black[0],black[1],black[2]))

        # We sweep through our world dictionary, drawing the world from the inputs.
        for block in self.model.world:
            value = self.model.world[block]
            temp = pygame.Rect(value.x,value.y,value.side,value.side)
            pygame.draw.rect(self.screen, pygame.Color(value.color[0],value.color[1],value.color[2]),temp)
        if model.endmode == True:
            # Draws save button.
            screen.blit(saveimage,(ref,3*ref))
        else:
            temp = pygame.Rect(ref,3*ref,ref,ref)
            pygame.draw.rect(self.screen, pygame.Color(0,0,0),temp)

        # Draws load button.
        screen.blit(loadimage,(ref,5*ref))

        if model.playmode == True:
            # Draws player.
            # temp = pygame.Rect(self.model.player.x,self.model.player.y,self.model.player.side,self.model.player.side)
            # pygame.draw.rect(self.screen, pygame.Color(playercolor[0],playercolor[1],playercolor[2]),temp)
            screen.blit(bob, (self.model.player.x, self.model.player.y))

            # Draws hidden rectangle.
            temp = pygame.Rect(3*ref,ref,len(model.palette)*2*ref,ref)
            pygame.draw.rect(self.screen, pygame.Color(0,0,0),temp)

            # Draws pause button.
            screen.blit(pausebutton,(ref,ref))
        else:
            # Draws play button.
            screen.blit(playbutton,(ref,ref))

        pygame.display.update()

        # Keep time constant.
        clock.tick(60)

class PyGamePathController:
    """
    Handles keyboard inputs.
    """
    def __init__(self,model,speed):
        self.model = model
        self.playbuild = model.playbuild
        self.speed = speed

    def handle_keyboard_event(self, event):
        local_area = model.update()
        state = 'node'                #default input should be processed as if our character were on a Node block.

        if event.key == pygame.K_ESCAPE:
            self.model.choice = None  # if Escape is pressed, delete and stored block type to place.
        if event.key == pygame.K_r:   # if r is pressed, it moves our cahracter to start, excluding the one in our palette.
            for block in self.model.world:
                if str(self.model.world[block].__class__) == '__main__.Start':
                    if block[1] == ref:
                        pass
                    else:
                        self.model.player.x = block[0] + .125*ref
                        self.model.player.y = block[1] + .125*ref
                        self.model.player.vx = 0
                        self.model.player.vy = 0
                else:
                    pass

        for block in local_area:
            if str(block.__class__) == '__main__.Ice':      # we can return here because inputs do not matter in the case of ice.
                return
            if str(block.__class__) == '__main__.Reverse':  # We use states to determine how to proceed with input processing.
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

    def handle_mouse_event(self, event):
        if event.type == MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            mx, my = roundpoint(mx, my)

            # Toggle button for play and pause mode.
            if mx == self.playbuild.x and my == self.playbuild.y:
                model.playmode = not model.playmode

            # Load.
            if mx == model.loadbutton.x and my == model.loadbutton.y:
                model.load()

            # Save.
            if model.endmode == True:
                if mx == model.savebutton.x and my == model.savebutton.y:
                    model.save()

            # Determines what to do depending on playmode.
            if model.playmode == True:
                for block in model.world:
                    if str(model.world[block].__class__) == '__main__.Start':
                        if block[1] == ref:
                            pass
                        else:
                            model.player.x = block[0] + .125*ref
                            model.player.y = block[1] + .125*ref
                            model.player.vx = 0.0
                            model.player.vy = 0.0
            else:
                model.endmode = False
                if self.model.choice == None: # if no block type is stored, then default to a node input.
                    self.model.choice = Node(self.model,mx,my)   
                    model.placeitem(self.model.choice,mx,my)
                else:
                    if (mx, my) in model.palette:
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