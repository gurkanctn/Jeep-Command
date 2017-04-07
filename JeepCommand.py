# Jeep Command
# Dev Start Date: 23 March 2017, Thursday
# find it on GitHub
# Licence : XXX
import os
import pygame as pg
from pygame.locals import *
import sys
import time

# set up the colors
Black    = (   0,   0,   0)
White    = ( 255, 255, 255)
Green    = (   0, 255,   0)
Red      = ( 255,   0,   0)
Blue     = (   0,   0, 255)
Gray     = ( 127, 127, 127)

GameVersion = "v0.02"

# set up Game Window constants
CAPTION = "Jeep Command " + GameVersion
SCREEN_SIZE = (800,600)

# set up graph window
pg.init()
pg.display.set_caption(CAPTION)
windowSurface = pg.display.set_mode(SCREEN_SIZE,0,32)

print("Jeep Command " + GameVersion +", loading...\n___ENJOY!___") # GAME Loading (supposedly)

# draw a polygon on screen and wait for 2 seconds
windowSurface.fill(Gray)
pg.draw.polygon(windowSurface, Black, ((200,38),(342,250),(200,402),(58,250)))
pg.draw.polygon(windowSurface, White, ((200,40),(200,250),(60,250)))
pg.draw.polygon(windowSurface, Blue , ((200,40),(200,250),(340,250)))
pg.draw.polygon(windowSurface, Green, ((200,250),(200,400),(60,250)))
pg.draw.polygon(windowSurface, Red,   ((200,250),(200,400),(340,250)))

pg.display.update()
#time.sleep(2)

# Background Music
pg.mixer.init()
#pg.mixer.music.load("bgmusic.mp3")
pg.mixer.music.load("Jeep_Command.wav")
pg.mixer.music.play(loops = -1)

#Some more game Constants
length_level = 10000


class _Physics(object):
    """A simplified physics class. Psuedo-gravity is often good enough."""
    def __init__(self):
        """You can experiment with different gravity here."""
        self.x_vel = 2
        self.y_vel = 0
        self.grav = 0.4
        self.fall = False
        self.x_vel_min=2
        self.x_vel_max=4
        
    def physics_update(self):
        """If the player is falling, add gravity to the current y velocity."""
        if self.fall:
            self.y_vel += self.grav
        else:
            self.y_vel = 0

class Block(pg.sprite.Sprite):
    """A class representing solid obstacles."""
    def __init__(self, color, rect):
        """The color is an (r,g,b) tuple; rect is a rect-style argument."""
        pg.sprite.Sprite.__init__(self)
        self.rect = pg.Rect(rect)
        self.image = pg.Surface(self.rect.size).convert()
        self.image.fill(color)
        self.type = "normal"

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
        #self.image.fill(pg.Color("red"))
        self.image = pg.image.load("Jeep.png").convert_alpha() # DENEME, işe yaradı ama uçuyor.
        self.rect = self.image.get_rect(topleft=location)
        self.speed = speed
        self.jump_power = -9.0
        self.jump_cut_magnitude = -3.0
        self.on_moving = False
        self.collide_below = False # False idi, deneme

    def check_keys(self, keys):
        """Find the player's self.x_vel based on currently held keys."""
        self.x_vel = self.x_vel_min
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.x_vel -= self.speed
            if self.x_vel <=self.x_vel_min:
                    self.x_vel = self.x_vel_min
        elif keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.x_vel += self.speed
            if self.x_vel >=self.x_vel_max:
                    self.x_vel = self.x_vel_max
        elif keys[pg.K_LSHIFT] or keys[pg.K_RSHIFT]:
            self.x_vel -= self.x_vel_min*2
            #if self.x_vel <=-self.x_vel_max:
            #        self.x_vel = -self.x_vel_min
    def get_position(self, obstacles):
        """Calculate the player's position this frame, including collisions."""
        if not self.fall:
            self.check_falling(obstacles)
        else:
            self.fall = self.check_collisions((0,self.y_vel), 1, obstacles)
        if self.x_vel:
            self.check_collisions((self.x_vel,0), 0, obstacles)

    def check_falling(self, obstacles):
        """If player is not contacting the ground, enter fall state."""
        if not self.collide_below:
            self.fall = True   # TRUE idi, 29 mart 23:06'da değiştirdim. Denemek için.
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
        self.rect.move_ip((0,-1))
        return collide

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
        #self.check_moving(obstacles)

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
        self.player = Player((80,858), 4) #50,875 idi
        self.viewport = self.screen.get_rect()
        self.level = pg.Surface((length_level,1000)).convert() #2000,1000 idi
        self.level_rect = self.level.get_rect()
        # self.win_text,self.win_rect = self.make_text()
        self.obstacles = self.make_obstacles()
    def make_obstacles(self):
        """Adds some arbitrarily placed obstacles to a sprite.Group."""
        walls = [Block(pg.Color("chocolate"), (0  ,980, length_level,  20)), #alt zemin
                 Block(pg.Color("chocolate"), (0 , 0 ,  20 , 1000)), #solduvar
                 Block(pg.Color("white"), (length_level-20, 0 ,  20 , 1000)) #sağduvar
                 ]
        static = [
                  Block(pg.Color("darkgreen"), (250,900,200,80)),
                  Block(pg.Color("darkgreen"), (450,800,200,80)),
                  Block(pg.Color("darkgreen"), (600,900,150,80)),
                  Block(pg.Color("darkgreen"), (1400,900,200,80)),
                  Block(pg.Color("darkgreen"), (2000,900,200,80)),
                  Block(pg.Color("darkgreen"), (2600,900,200,80)),
                  Block(pg.Color("darkgreen"), (4000,900,200,80)),
                  Block(pg.Color("darkgreen"), (6000,900,200,80)),
                  Block(pg.Color("darkgreen"), (9000,360,880,40)),
                  #Block(pg.Color("darkgreen"), (950,400,30,20)),
                  #Block(pg.Color("darkgreen"), (20,630,50,20)),
                  #Block(pg.Color("darkgreen"), (80,530,50,20)),
                  #Block(pg.Color("darkgreen"), (130,470,200,215)),
                  #Block(pg.Color("darkgreen"), (20,760,30,20)),
                  #Block(pg.Color("darkgreen"), (400,740,30,40))
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
        self.update_viewport()

    def draw(self):
        """
        Draw all necessary objects to the level surface, and then draw
        the viewport section of the level to the display surface.
        """
        self.level.fill(pg.Color("lightblue"))
        self.obstacles.draw(self.level)
        #self.level.blit(self.win_text, self.win_rect)
        self.player.draw(self.level)
        self.screen.blit(self.level, (0,0), self.viewport)

    def main_loop(self):
        """As simple as it gets."""
        while not self.done:
            for event in pg.event.get():
                if event.type == QUIT:
                    self.done = True
                    print(" Game over... \n Thanks for playing Jeep Command!") # GAME OVER.
                    pg.quit()
                    sys.exit()
                else:
                    if event.type == pg.KEYDOWN:
                        if event.key == pg.K_SPACE:
                            self.player.jump(self.obstacles)
                            boing_sound=pg.mixer.Sound("chimes.wav").play()
                    if event.type == MOUSEBUTTONDOWN:
                        #pg.mixer.music.set_volume(0.8*pg.mixer.music.get_volume())
                        boing_sound=pg.mixer.Sound("chimes.wav").play()
                        #pg.mixer.music.set_volume(1.25*pg.mixer.music.get_volume())
                        #pg.mixer.fadeout(3) # stop playing sounds/and bg music
                        #print ("stopped playing, mouse clicked?")
                        #print(pg.mixer.music.get_volume())
            #self.event_loop()
            self.update()
            self.draw()
            pg.display.update()
            self.clock.tick(self.fps)
 #          self.display_fps()
 #          timePrevious = time.process_time()
            #i=math.fmod(i+3,255)
            dynamicColor = (128,128,128)
            windowSurface.fill(dynamicColor)      
 #           pg.display.update()
 #           dTime = time.process_time()-timePrevious
 #           if dTime < 0.04:
 #               time.sleep(0.04-dTime)
        
if __name__ == "__main__":
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pg.init()
    pg.display.set_caption(CAPTION)
    pg.display.set_mode(SCREEN_SIZE)
    run_it = Control()
    run_it.main_loop()
   # pg.quit()
   # sys.exit()

