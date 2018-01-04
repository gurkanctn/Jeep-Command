# Jeep Command
# Dev Start Date: 23 March 2017, Thursday
# find it on GitHub
# Licence : XXX
import os
import pygame as pg
from pygame.locals import *
from random import *
import sys
import time

# set up the colors
Black    = (   0,   0,   0)
White    = ( 255, 255, 255)
Green    = (   0, 255,   0)
Red      = ( 255,   0,   0)
Blue     = (   0,   0, 255)
Gray     = ( 127, 127, 127)

GameVersion = "v0.04"

# set up Game Window constants
CAPTION = "Jeep Command " + GameVersion
SCREEN_SIZE = (800,600)

# set up graph window
pg.init()
pg.display.set_caption(CAPTION)
windowSurface = pg.display.set_mode(SCREEN_SIZE,0,32)

print("Jeep Command " + GameVersion +", loading...\n___ENJOY!___") # GAME Loading (supposedly)

# draw a polygon on screen and ## wait for 2 seconds
windowSurface.fill(Gray)
pg.draw.polygon(windowSurface, Black, ((200,38),(342,250),(200,402),(58,250)))
pg.draw.polygon(windowSurface, White, ((200,40),(200,250),(60,250)))
pg.draw.polygon(windowSurface, Blue , ((200,40),(200,250),(340,250)))
pg.draw.polygon(windowSurface, Green, ((200,250),(200,400),(60,250)))
pg.draw.polygon(windowSurface, Red,   ((200,250),(200,400),(340,250)))

pg.display.update()
time.sleep(2)

# Background Music
pg.mixer.init()
pg.mixer.music.load("Jeep_Command.wav")
pg.mixer.music.play(loops = -1)

#Some more game Constants
length_level = 10000

def text_to_screen(self, text, x, y, size = 50,
            color = (200, 000, 000), font_type = 'myfont.ttf'):
    try:
        text = str(text)
        #text = str('123456')
        #print (text)
        font = pg.font.Font(font_type, size)
        text2 = font.render(text, True, color)
        self.screen.blit(text2, (x, y))

    except Exception as e:
        print ('Font Error, saw it coming')
        raise e

class _Physics(object):
    """A simplified physics class. Psuedo-gravity is often good enough."""
    def __init__(self):
        """You can experiment with different gravity here."""
        self.x_vel = 0
        self.y_vel = 0
        self.grav = 0.3
        self.fall = False
        self.x_vel_min=1
        self.x_vel_max=+3
        
    def physics_update(self):
        """If the player is falling, add gravity to the current y velocity."""
        if self.fall:
            self.y_vel += self.grav
        else:
            self.y_vel = 0

# todo: clouds class'ını düzgün biçimde ekle..

class Clouds(pg.sprite.Sprite):
    """A class to include and animate clouds"""
    def __init__(self, color, rect):
        """initialize the cloud"""
        pg.sprite.Sprite.__init__(self)
        self.x = random()*legth_level
        self.x_vel = random()*5
        self.rect = pg.Rect(rect)
        self.image = pg.Surface(self.rect.size).convert()
        self.image.fill(color)
        self.type = "normal"
        self.mask=pg.mask.from_surface(self.image)

    def clouds_update(self):
        if self.x >= 0:
            self.x = self.x - self.x_vel
            if self.x < 0:
                # KILL THIS CLOUD AND GENERATE NEW ONE
                display("cloud dead")
                
class Block(pg.sprite.Sprite):
    """A class representing solid obstacles."""
    def __init__(self, color, rect):
        """The color is an (r,g,b) tuple; rect is a rect-style argument."""
        pg.sprite.Sprite.__init__(self)
        self.rect = pg.Rect(rect)
        self.image = pg.Surface(self.rect.size).convert()
        self.image.fill(color)
        self.type = "normal"
        self.mask=pg.mask.from_surface(self.image)

class Player(_Physics, pg.sprite.Sprite):
    """Class representing our player."""
    def __init__(self,location,speed):
        """
        The location is an (x,y) coordinate pair, and speed is the player's
        speed in pixels per frame. Speed should be an integer.
        """
        _Physics.__init__(self)
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface((30,55)).convert()
        self.image = pg.image.load("Jeep.png").convert_alpha()
        self.rect = self.image.get_rect(topleft=location)
        self.mask=pg.mask.from_surface(self.image)
        self.speed = speed
        self.jump_power = -9.0
        self.jump_cut_magnitude = -6.0
        self.on_moving = False
        self.collide_below = False

    def check_keys(self, keys):
        """Find the player's self.x_vel based on currently held keys."""
        self.x_vel = self.x_vel_min
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.x_vel -= self.speed
            if self.x_vel <=self.x_vel_min:
                    self.x_vel = self.x_vel_min
        elif keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.x_vel += 1
            if self.x_vel >=self.x_vel_max:
                    self.x_vel = self.x_vel_max
        elif keys[pg.K_LSHIFT] or keys[pg.K_RSHIFT]:
            self.x_vel -= self.x_vel_min*2

    def get_position(self, obstacles):
        """Calculate the player's position this frame, including collisions."""
        if not self.fall:
            self.check_falling(obstacles)
        else:
            self.fall = self.check_collisions((0,self.y_vel), 1, obstacles)
        if self.x_vel:
            self.check_collisions((self.x_vel,0), 0, obstacles)
            if not self.check_collisions((self.x_vel,0), 0, obstacles):
                print(" You lose! Try Again! \n Thanks for playing Jeep Command!") # GAME OVER.
                pg.mixer.music.stop() # stop playing sounds/and bg music! DOESNT WORK!
                time.sleep(1)
                boing_sound=pg.mixer.Sound("chimes.wav").play()
                time.sleep(1)
                pg.quit()
                sys.exit()
    def check_falling(self, obstacles):
        """If player is not contacting the ground, enter fall state."""
        if not self.collide_below:
            self.fall = True
            self.on_moving = False
        
    def check_collisions(self, offset, index, obstacles):
        """
        This function checks if a collision would occur after moving offset
        pixels. If a collision is detected, the position is decremented by one
        pixel and retested. This continues until we find exactly how far we can
        safely move, or we decide we can't move.
        """
        unaltered = True
        self.rect[index] += offset[index]
        while pg.sprite.spritecollideany(self, obstacles):
            self.rect[index] += (1 if offset[index]<0 else -1)
            unaltered = False
        return unaltered

    def check_above(self, obstacles):
        """When jumping, don't enter fall state if there is no room to jump."""
        self.rect.move_ip(0, -1)
        collide = pg.sprite.spritecollideany(self, obstacles)
        self.rect.move_ip(0, 1)
        return collide

    def check_below(self, obstacles):
        """Check to see if the player is contacting the ground."""
        self.rect.move_ip((0,1))  # move_ip = Move in Place
        collide = pg.sprite.spritecollide(self, obstacles, False)
        coll=False
        if collide:
            coll = pg.sprite.spritecollide(self, obstacles, False, pg.sprite.collide_mask)
        self.rect.move_ip((0,-1))
        #print (coll)
        return not coll

    def jump(self, obstacles):
        """Called when the user presses the jump button."""
        if not self.fall and not self.check_above(obstacles):
            self.y_vel = self.jump_power
            self.fall = True
            self.on_moving = False

    def jump_cut(self):
        """Called if player releases the jump key before maximum height."""
        if self.fall:
            if self.y_vel < self.jump_cut_magnitude:
                self.y_vel = self.jump_cut_magnitude

    def pre_update(self, obstacles):
        """Ran before platforms are updated."""
        self.collide_below = self.check_below(obstacles)

    def update(self, obstacles, keys):
        """Everything we need to stay updated; ran after platforms update."""
        self.check_keys(keys)
        self.get_position(obstacles)
        self.physics_update()
        
    def draw(self, surface):
        """Blit the player to the target surface."""
        surface.blit(self.image, self.rect)

class Control(object):
    """Class for managing event loop and game states."""
    def __init__(self):
        """Initalize the display and prepare game objects."""
        self.screen = pg.display.get_surface()
        self.screen_rect = self.screen.get_rect()
        self.clock = pg.time.Clock()
        self.fps = 60.0
        self.keys = pg.key.get_pressed()
        self.done = False
        self.player = Player((50,858), 4) #50,875 idi
        self.viewport = self.screen.get_rect()
        self.level = pg.Surface((length_level,1000)).convert() #2000,1000 idi
        self.level_rect = self.level.get_rect()
        self.obstacles = self.make_obstacles()
        self.color=128
        self.score = 0
        #self.clouds = self.make_clouds()

    def make_clouds(self):
        cloudsList = [Block(pg.Color("chocolate"), (0  ,980, length_level,  20)), #alt zemin
                 Block(pg.Color("chocolate"), (0 , 0 ,  20 , 1000)), #solduvar
                 Block(pg.Color("white"), (length_level-20, 0 ,  20 , 1000)) #sağduvar
                 ]
        return pg.sprite.Group(cloudsList)
    
    def make_obstacles(self):
        """Adds some arbitrarily placed obstacles to a sprite.Group."""
        walls = [Block(pg.Color("chocolate"), (0  ,980, length_level,  20)), #alt zemin
                 Block(pg.Color("chocolate"), (0 , 0 ,  20 , 1000)), #solduvar
                 Block(pg.Color("white"), (length_level-20, 0 ,  20 , 1000)) #sağduvar
                 ]
        static = [
                  Block(pg.Color("darkgreen"), (450,900,40,80)),
                  Block(pg.Color("darkgreen"), (650,800,40,80)),
                  Block(pg.Color("darkgreen"), (800,900,40,80)),
                  Block(pg.Color("darkgreen"), (1400,900,200,80)),
                  Block(pg.Color("darkgreen"), (2000,900,200,80)),
                  Block(pg.Color("darkgreen"), (2600,900,200,80)),
                  Block(pg.Color("darkgreen"), (4000,900,200,80)),
                  Block(pg.Color("darkgreen"), (6000,900,200,80)),
                  Block(pg.Color("darkgreen"), (9000,360,880,40)),
                  ]
        return pg.sprite.Group(walls, static)

    def update_viewport(self):
        """
        The viewport will stay centered on the player unless the player
        approaches the edge of the map.
        """
        self.viewport.center = self.player.rect.center
        self.viewport.clamp_ip(self.level_rect)


    def update(self):
        """Update the player, obstacles, and current viewport."""
        self.keys = pg.key.get_pressed()
        self.player.pre_update(self.obstacles)
        self.obstacles.update(self.player, self.obstacles)
        self.player.update(self.obstacles, self.keys)
        #self.cloud.update(self.obstacles, self.keys) #update clouds
        self.update_viewport()
        
        #print ("Score: " , self.score)
        self.score +=1
        
    def draw(self):
        """
        Draw all necessary objects to the level surface, and then draw
        the viewport section of the level to the display surface.
        """
        self.color = (self.color +1)%255
        dynamicColor = (self.color,128,128)
        self.level.fill(dynamicColor)
        self.obstacles.draw(self.level)
        self.player.draw(self.level)
        #self.cloud.draw(self.level)  # draw clouds
        self.screen.blit(self.level, (0,0), self.viewport)
        text_to_screen(self, 'Score: {0}'.format(self.score), 550, 10)

    def main_loop(self):
        """As simple as it gets."""
        while not self.done:
            for event in pg.event.get():
                if event.type == QUIT:
                    self.done = True
                    print(" You quit! Come back... \n Thanks for playing Jeep Command!") # GAME OVER.
                    pg.quit()
                    sys.exit()
                else:
                    if event.type == pg.KEYDOWN:
                        if event.key == pg.K_SPACE:
                            self.player.jump(self.obstacles)
                            boing_sound=pg.mixer.Sound("chimes.wav").play()
                    if event.type == MOUSEBUTTONDOWN:
                        boing_sound=pg.mixer.Sound("chimes.wav").play()

            self.update()
            self.draw()
            pg.display.update()
            self.clock.tick(self.fps)
        
if __name__ == "__main__":
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pg.init()
    pg.display.set_caption(CAPTION)
    pg.display.set_mode(SCREEN_SIZE)
    run_it = Control()
    run_it.main_loop()
