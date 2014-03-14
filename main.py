################################################################################
#
#   Copyright (C) , 2013 Ahmad Elhedek (aelhedek1@cougars.com)
#   
#   Permission to use, copy, modify, and distribute this software for any
#   purpose with or without fee is hereby granted, provided that the above
#   copyright notice and this permission notice appear in all copies.

#   The software is provided "as is" and the author disclaims all warranties
#   with regard to this software including all implied warranties of
#   merchantability and fitness. In no event shall the author be liable for
#   any special, direct, indirect, or consequential damages or any damages
#   whatsoever resulting from loss of use, data or profits, whether in an
#   action of contract, negligence or other tortious action, arising out of
#   or in connection with the use or performance of this software.
#
################################################################################


import pygame, sys, random, math, parallax
from pygame.locals import *

random.seed()
pygame.init()
pygame.mouse.set_visible(0) #hide mouse


WIDTH = 780
HEIGHT = 580
BALL_RADIUS = 10
BALL_COLOR = (255,0,0)
BALL_ACCEL = 0.03
BALL_SPEED = 0.9
BALL_SPEED_DIMINISH = 0.05
BALL_START_LOC = [WIDTH/2 ,HEIGHT]
BALL_JUMP_SPEED_LIMIT = 1.4
JUMP_CHARGE_INTERVAL = 0.02
MOVE_TICK_MAX = 1.5
MOVE_TICK = 0.2
JUMP_SENSITIVITY = 8*(2*BALL_RADIUS)
SHELF_THICKNESS = 10
SHELF_MIN_WIDTH = 50
SHELF_MAX_WIDTH = 100
BENIFIT_FROM_BOOST_FACTOR = 0.05
BG_WIDTH = 300
BG_HEIGHT = 300
LIVES = 3

def main():
    cam = Camera(WIDTH, HEIGHT)
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Ball & the Beanstalk')

    clock = pygame.time.Clock()


    all_balls = pygame.sprite.GroupSingle()
    all_collison_rects = pygame.sprite.GroupSingle()
    all_shelfs = pygame.sprite.Group()
    all_status_bars_back = pygame.sprite.Group()
    all_status_bars_front = pygame.sprite.Group()
    all_trigger_booms = pygame.sprite.Group()
    all_rest = pygame.sprite.Group()
    all_score_boards = pygame.sprite.GroupSingle()


    #building bg image
    bg = parallax.ParallaxSurface()
    bg.add('images/clouds.jpg', 4, WIDTH, HEIGHT)
    bg.add('images/beanstalk1.png', 1, WIDTH, HEIGHT)


    all_balls.add(Ball(HEIGHT))
    my_ball = all_balls.sprites() #use my_ball[0]
    all_collison_rects.add(Collison_Ball_Rect())
    all_status_bars_back.add(Charge_Bar_Back())
    all_status_bars_front.add(Charge_Bar_Front())
    all_score_boards.add(Score_Display())
    my_score_board = all_score_boards.sprites() #user my_score_board[0]

    #making lives
    lives = LIVES
    life_list = []
    for i in xrange(lives):
        life_list.append(Life_Display(160+ (40*i)))

    all_status_bars_front.add(life_list)


    #making shelfs
    group_number = 1
    group_name = 'group' + str(group_number)
    globals()[group_name] = []

    build_lvl = HEIGHT - 150
    #group A
    for i in xrange(100):
        wid = random.randint(SHELF_MIN_WIDTH,SHELF_MAX_WIDTH)
        pos = [random.randint(0, WIDTH-wid), random.randint(build_lvl-40, build_lvl), wid]
        new_shelf = Shelf(pos[0],pos[1], pos[2])
        globals()[group_name].append(new_shelf)
        build_lvl = build_lvl - 80

    all_shelfs.add(globals()[group_name])

    group_number += 1
    group_name = 'group' + str(group_number)
    globals()[group_name] = []

    intitial_lvl_height = build_lvl
    #group B
    for i in xrange(100):
        wid = random.randint(SHELF_MIN_WIDTH,SHELF_MAX_WIDTH)
        pos = [random.randint(0, WIDTH-wid), random.randint(build_lvl-40, build_lvl), wid]
        new_shelf = Shelf(pos[0],pos[1], pos[2])
        globals()[group_name].append(new_shelf)
        build_lvl = build_lvl - 80

    all_shelfs.add(globals()[group_name])

    last_lvl_height = build_lvl - intitial_lvl_height

    #printing debugging only
    #print 'total height: ', abs(build_lvl)
    #print 'group: ', group_name
    #print 'last level height: ', abs(last_lvl_height)
    #print 'finished initialization'

    while True:
        delta = clock.tick(60)
        
        #camera and ball ajusting
        cam.chase_mode = False
        if (my_ball[0].y <= 100):
            cam.chase(my_ball[0].speedy, delta)
            my_ball[0].shift_ball(100)
            cam.chase_mode = True



        #camera
        cam.update(my_ball[0])


        #update events

        if (abs(my_ball[0].speedy)> BALL_ACCEL) and ((my_ball[0].speedy) < 0) and cam.chase_mode:
            mov_y_speed = my_ball[0].speedy
        else:
            mov_y_speed = 0

        bg.scroll(mov_y_speed)
        all_balls.update(delta, cam)
        all_collison_rects.update(my_ball[0].x, my_ball[0].y, my_ball[0].speedy)
        all_status_bars_front.update(my_ball[0].charge_jump_speed)
        all_shelfs.update(cam)
        all_rest.update(cam)
        all_trigger_booms.update(cam)  
        all_score_boards.update(cam.state.top)      

              
        #collide
        for s in all_shelfs.sprites():
            if pygame.sprite.spritecollideany(s, all_trigger_booms):
                all_rest.add(Shelf_Boom(s.rect.center[0], s.rect.top, cam ))
                s.kill()
                my_score_board[0].style_bonus += 5
            #don't bother unless ball IS FALLING
            if (my_ball[0].speedy > 0):
                if (pygame.sprite.collide_rect(all_collison_rects.sprite, s)):
                    #now set the ball's floor to the height of the shelf
                    my_ball[0].min_height = int(s.rect.top)
                    my_ball[0].speedy = - abs(my_ball[0].speedy-(BALL_SPEED_DIMINISH*abs(my_ball[0].speedy)))
                    #if space is pressed, jump, MECHANICS
                    if (my_ball[0].charge_jump_speed > 0.75*BALL_JUMP_SPEED_LIMIT):
                        my_ball[0].jump(delta)
                        all_rest.add(Shelf_Boom(s.rect.center[0], s.rect.top, cam ))
                        new_thingy = Land_Boom(my_ball[0].rect.left, my_ball[0].rect.top, cam )
                        new_thingy.update(cam)
                        all_trigger_booms.add(new_thingy)
                        new_thingy = Launch_Boom(my_ball[0].rect.left, my_ball[0].rect.top, cam )
                        new_thingy.update(cam)
                        all_trigger_booms.add(new_thingy)
            
            
        if not pygame.sprite.spritecollideany(all_collison_rects.sprite, all_shelfs):
            my_ball[0].min_height = cam.state.bottom

        
        #Die Once
        if (cam.started_scrolling) and (my_ball[0].rect.bottom >= HEIGHT):
            my_ball[0].respawn()
            #deleting 1 life
            lives -= 1
            all_status_bars_front.remove(life_list)
            try:
                life_list.pop()
            except:
                break
            all_status_bars_front.add(life_list)   


        #event handler
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if ((pygame.sprite.spritecollideany(all_collison_rects.sprite, all_shelfs)) or (distance_between(my_ball[0].x, my_ball[0].y, my_ball[0].x, my_ball[0].min_height) <= JUMP_SENSITIVITY)):
                        my_ball[0].jump(delta)
                        #produce jump animation
                        new_thingy = Launch_Boom(my_ball[0].rect.left, my_ball[0].rect.top, cam )
                        new_thingy.update(cam)
                        all_trigger_booms.add(new_thingy)
            if event.type == QUIT:
                sys.exit(0)
        
    
        #shelf maintaince
        if cam.state.top > (abs(build_lvl) - abs(last_lvl_height/2)):
            #New Group
            group_number += 1
            group_name = 'group' + str(group_number)
            globals()[group_name] = []

            intitial_lvl_height = build_lvl
            for i in xrange(100):
                wid = random.randint(SHELF_MIN_WIDTH,SHELF_MAX_WIDTH)
                pos = [random.randint(0, WIDTH-wid), random.randint(build_lvl-40, build_lvl), wid]
                new_shelf = Shelf(pos[0],pos[1], pos[2])
                globals()[group_name].append(new_shelf)
                build_lvl = build_lvl - 80
            
            last_lvl_height = build_lvl - intitial_lvl_height
            all_shelfs.add(globals()[group_name])

            #printing debugging only
            #print 'created: ', group_name

            #delete previous, previous group
            group_name_to_delete = 'group' + str(group_number-2)
            all_shelfs.remove(globals()[group_name_to_delete])
            #printing debugging only
            #print 'removed: ', group_name_to_delete

        
        #draw
        bg.draw(screen)
        all_shelfs.draw(screen)
        
        #drawing debugging only
        #all_collison_rects.draw(screen)
        
        all_balls.draw(screen)
        all_rest.draw(screen)
        all_trigger_booms.draw(screen)
        all_status_bars_back.draw(screen)
        all_status_bars_front.draw(screen)
        all_score_boards.draw(screen)

        pygame.display.flip()
    
    final_text = pygame.sprite.Group()
    final_text.add(Final_Score_Display(my_score_board[0].current_lvl_prog, my_score_board[0].style_bonus))
    final_text.add(Game_Over_Display())
    final_text.add(Score_Is_Display())
    time_passed = 0
    ticker = pygame.time.Clock()
    while True:
        delta = clock.tick(60)
        ticker.tick(1)
        time_passed += ticker.get_time()

        screen.fill((0,0,0))
        final_text.draw(screen)
        pygame.display.flip()
        
        if (time_passed > 6000):
            sys.exit(0)


############################################################################################################
class Score_Is_Display(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.font = pygame.font.Font(None, 70)
        self.x = WIDTH/2 - 140
        self.y = HEIGHT/2 - 100
        self.text  = "Your Score is"
        self.image = self.font.render(str(self.text), 1, (255,255,255))
        self.rect = self.image.get_rect()
        self.rect.top, self.rect.left = self.y, self.x

class Game_Over_Display(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.font = pygame.font.Font(None, 70)
        self.x = WIDTH/2 - 120
        self.y = HEIGHT/2 - 150
        self.text  = "Game Over"
        self.image = self.font.render(str(self.text), 1, (255,255,255))
        self.rect = self.image.get_rect()
        self.rect.top, self.rect.left = self.y, self.x


class Final_Score_Display(pygame.sprite.Sprite):
    def __init__(self, lvl_prog, style_bonus):
        pygame.sprite.Sprite.__init__(self)
        self.font = pygame.font.Font(None, 70)
        self.x = WIDTH/2 - 10
        self.y = HEIGHT/2 - 20
        self.style_bonus = style_bonus
        self.current_lvl_prog = lvl_prog
        self.score = (self.current_lvl_prog/100) + self.style_bonus
        self.image = self.font.render(str(self.score), 1, (255,255,255))
        self.rect = self.image.get_rect()
        self.rect.top, self.rect.left = self.y, self.x

class Score_Display(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.font = pygame.font.Font(None, 70)
        self.x = 0 + 10
        self.y = 0
        self.score  = 0
        self.style_bonus = 0
        self.current_lvl_prog = 0
        self.image = self.font.render(str(self.score), 1, (0,0,255))
        self.rect = self.image.get_rect()
        self.rect.top, self.rect.left = self.y, self.x

    def update(self, lvl_prog):
        if lvl_prog > self.current_lvl_prog:
            self.current_lvl_prog = lvl_prog
        self.score = (self.current_lvl_prog/100) + self.style_bonus
        self.image = self.font.render(str(self.score), 1, (0,0,255))
        self.rect = self.image.get_rect()
        self.rect.top, self.rect.left = self.y, self.x

class Life_Display(pygame.sprite.Sprite):
    def __init__(self, y):
        pygame.sprite.Sprite.__init__(self)
        radius = 10
        size = 2 * radius
        self.rad = radius
        self.x, self.y = WIDTH - 35, y 


        self.image = pygame.Surface((size, size), pygame.SRCALPHA, 32)
        self.image = self.image.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = self.x, self.y
        pygame.draw.circle(self.image, BALL_COLOR, (radius, radius), radius)

    def update(self, _):
        pass


class Camera(object):
    def __init__(self, width, height):
        self.started_scrolling = False
        self.chase_mode = False
        self.width = width
        self.height = height
        self.orginal_ball_y = BALL_START_LOC[1]
        self.state = Rect(0, self.orginal_ball_y, self.width , self.height)

    def update(self, target):
        new_state = Rect(0, self.orginal_ball_y - target.rect.top, self.width, self.height)
        if (new_state.top < self.state.top):
            self.state = new_state

    def chase(self, speedy, delta):
        self.started_scrolling = True
        increment =  -speedy*delta
        self.orginal_ball_y = self.orginal_ball_y + increment
        self.state = Rect(0, self.state.top + increment, self.width, self.height)

def distance_between(x1, y1, x2, y2):
    return (math.hypot(x2-x1, y2-y1))


class Shelf_Boom(pygame.sprite.Sprite):
    def __init__(self, x, y, cam):
        pygame.sprite.Sprite.__init__(self)
        self.x = x - 80 - cam.state.left
        self.y = y - 120 - cam.state.top
        self.loadImages()
        self.image = self.imageStand
        self.image = pygame.transform.scale(self.image, (180,150))
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = self.x, self.y
        self.frame = 0
        # increase delay value to slow down animation even more
        self.delay = 5
        self.pause = 0

    def update(self, cam):
        self.rect.left = self.x + cam.state.left
        self.rect.top = self.y + cam.state.top
        self.pause += 1
        if self.pause >= self.delay:
            #reset pause and advance animation
            self.pause = 0
            self.frame += 1
            #kill it if done with frames
            if self.frame >= len(self.objImages):
                self.kill()
                return
            self.image = self.objImages[self.frame]
            self.image = pygame.transform.scale(self.image, (180,150))
    def loadImages(self):
        self.imageStand = pygame.image.load("images/exp1.png").convert()
        self.imageStand = self.imageStand.convert()
        transColor = self.imageStand.get_at((1, 1))
        self.imageStand.set_colorkey(transColor)

        self.objImages = []
        for i in xrange(1,19):
            imgName = "images/exp%d.png" % i
            tmpImage = pygame.image.load(imgName).convert()
            tmpImage = tmpImage.convert()
            transColor = tmpImage.get_at((1, 1))
            tmpImage.set_colorkey(transColor)
            self.objImages.append(tmpImage)

class Land_Boom(pygame.sprite.Sprite):
    def __init__(self, x, y, cam):
        pygame.sprite.Sprite.__init__(self)
        self.x = x - 52 - cam.state.left
        self.y = y - 122 - cam.state.top
        self.loadImages()
        self.image = self.imageStand
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = self.x, self.y
        self.frame = 0
        # increase delay value to slow down animation even more
        self.delay = 5
        self.pause = 0

    def update(self, cam):
        self.rect.left = self.x + cam.state.left
        self.rect.top = self.y + cam.state.top
        self.pause += 1
        if self.pause >= self.delay:
            #reset pause and advance animation
            self.pause = 0
            self.frame += 1
            #kill it if done with frames
            if self.frame >= len(self.objImages):
                self.kill()
                return
            self.image = self.objImages[self.frame]
        

    def loadImages(self):
        self.imageStand = pygame.image.load("images/boom1.png").convert()
        self.imageStand = self.imageStand.convert()
        transColor = self.imageStand.get_at((1, 1))
        self.imageStand.set_colorkey(transColor)

        self.objImages = []
        for i in xrange(1,25):
            imgName = "images/boom%d.png" % i
            tmpImage = pygame.image.load(imgName).convert()
            tmpImage = tmpImage.convert()
            transColor = tmpImage.get_at((1, 1))
            tmpImage.set_colorkey(transColor)
            self.objImages.append(tmpImage)


class Launch_Boom(pygame.sprite.Sprite):
    def __init__(self, x, y, cam):
        pygame.sprite.Sprite.__init__(self)
        self.x = x - 116 - cam.state.left
        self.y = y - 110 - cam.state.top
        self.loadImages()
        self.image = self.imageStand
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = self.x, self.y
        self.frame = 0
        # increase delay value to slow down animation even more
        self.delay = 5
        self.pause = 0

    def update(self, cam):
        self.rect.left = self.x + cam.state.left
        self.rect.top = self.y + cam.state.top
        self.pause += 1
        if self.pause >= self.delay:
            #reset pause and advance animation
            self.pause = 0
            self.frame += 1
            #kill it if done with frames
            if self.frame >= len(self.objImages):
                self.kill()
                return
            self.image = self.objImages[self.frame]
        

    def loadImages(self):
        self.imageStand = pygame.image.load("images/explode1.png").convert()
        self.imageStand = self.imageStand.convert()
        transColor = self.imageStand.get_at((1, 1))
        self.imageStand.set_colorkey(transColor)

        self.objImages = []
        for i in xrange(1,13):
            imgName = "images/explode%d.png" % i
            tmpImage = pygame.image.load(imgName).convert()
            tmpImage = tmpImage.convert()
            transColor = tmpImage.get_at((1, 1))
            tmpImage.set_colorkey(transColor)
            self.objImages.append(tmpImage)
        


class Collison_Ball_Rect(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.x, self.y = BALL_START_LOC
        self.size = 2*(BALL_RADIUS)
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA, 32)
        self.image = self.image.convert_alpha()
        self.image.fill((255,250,0))
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = self.x, self.y
    def update(self, x, y, speedy):
        self.x = x - ((self.size/2) - BALL_RADIUS)
        self.y = y
        new_size = self.size + int(self.size*abs(speedy))
        self.image = pygame.Surface((self.size, new_size), pygame.SRCALPHA, 32)
        self.image = self.image.convert_alpha()
        self.image.fill((255,250,0))
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = self.x, self.y


class Charge_Bar_Front(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.max_length = 100
        self.image = pygame.Surface((20, 0))
        self.rect = self.image.get_rect()
        self.image.fill((100,0,250))
        pygame.draw.line(self.image, (255,0,0), (0, 0.75*self.max_length), (20, 0.75*self.max_length),2)
        self.rect.left, self.rect.top = WIDTH - 35, 35

    def update(self, charge_jump_speed):

        length_to_fill = (float(charge_jump_speed)/ BALL_JUMP_SPEED_LIMIT) * self.max_length
        length_to_fill = int (length_to_fill)
        if (length_to_fill < 0):
            length_to_fill = 0
        self.image = pygame.Surface((20, length_to_fill))
        self.rect = self.image.get_rect()
        self.image.fill((0,0,255))
        pygame.draw.line(self.image, (255,0,0), (0, 0.75*self.max_length), (20, 0.75*self.max_length),2)
        self.rect.left, self.rect.top = WIDTH - 35, 35

class Charge_Bar_Back(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.max_length = 100
        self.image = pygame.Surface((20, self.max_length))
        self.rect = self.image.get_rect()
        self.image.fill((255,255,102))
        pygame.draw.line(self.image, (255,0,0), (0, 0.75*self.max_length), (20, 0.75*self.max_length),2)
        self.rect.left, self.rect.top = WIDTH - 35, 35

class Shelf(pygame.sprite.Sprite):
    def __init__(self, x, y, stretch):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('images/block.gif').convert()
        self.image = pygame.transform.scale(self.image, (stretch,SHELF_THICKNESS))
        self.x = x
        self.y = y

        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = self.x, self.y
    def update(self, cam):
        self.rect.left = self.x + cam.state.left
        self.rect.top = self.y + cam.state.top



class Ball(pygame.sprite.Sprite):
    def __init__(self, floor):
        pygame.sprite.Sprite.__init__(self)
        radius = BALL_RADIUS
        size = 2 * radius
        self.size = size
        self.rad = radius
        self.x, self.y = BALL_START_LOC
        self.speedx = BALL_SPEED
        self.speedy = 0
        self.ay = BALL_ACCEL
        self.charge_jump_speed = 0

        self.move_ticker = MOVE_TICK
        self.start_loc = self.y
        self.min_height = floor

        self.image = pygame.Surface((size, size), pygame.SRCALPHA, 32)
        self.image = self.image.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = self.x, self.y
        pygame.draw.circle(self.image, BALL_COLOR, (radius, radius), radius)

    def jump(self, delta):
        speed_inc = self.speedx * delta * self.move_ticker
        self.speedy = -self.charge_jump_speed - abs(speed_inc*BENIFIT_FROM_BOOST_FACTOR) 
        self.charge_jump_speed = 0

    def charge_jump(self):
        if (self.charge_jump_speed <= BALL_JUMP_SPEED_LIMIT):
            self.charge_jump_speed += JUMP_CHARGE_INTERVAL

    def diminish_charge_jump(self):
        if (self.charge_jump_speed > 0):
            self.charge_jump_speed -= JUMP_CHARGE_INTERVAL

    def update(self, delta, cam):
        keys = pygame.key.get_pressed()
        if ((keys[K_LEFT]) and (self.x - self.size  > 0)):
            if (self.move_ticker < MOVE_TICK_MAX):
                self.move_ticker += 0.01
            speed_inc = self.speedx * delta * self.move_ticker
            self.x -= speed_inc

        if ((keys[K_RIGHT]) and ((self.x + 2*self.size) < WIDTH)):
            if (self.move_ticker < MOVE_TICK_MAX):
                self.move_ticker += 0.01
            speed_inc = self.speedx * delta * self.move_ticker
            self.x += speed_inc

        if (keys[K_LCTRL]):
            self.charge_jump()

        if not (keys[K_LCTRL]):
            self.diminish_charge_jump()

        if (not(keys[K_LEFT]) and not (keys[K_RIGHT])) or ((keys[K_RIGHT]) and (keys[K_LEFT])):
            self.move_ticker = MOVE_TICK

        oldspeedy = self.speedy
        #only if it will not make the ball self.y go
        #over floor, min_height
        if (self.y < self.min_height):
            self.speedy += self.ay
        if (oldspeedy < 0) and (self.speedy > 0):
            self.rememberChangeDir()

        self.y += self.speedy * delta 
        self.rect.left, self.rect.top = self.x, self.y

        if (self.rect.bottom >= self.min_height) :
            self.speedy = - abs((self.speedy)- BALL_SPEED_DIMINISH*abs(self.speedy))
            self.rect.bottom = self.min_height
            self.rememberChangeDir()
        
    def shift_ball(self, y):
        self.y =  y
        self.rect.left, self.rect.top = self.x, self.y

    def rememberChangeDir(self):
        now = self.rect.bottom
        self.distance = self.start_loc - now
        if (self.distance < 0): 
            self.distance *= -1
        self.start_loc = now
    
    def respawn(self):
        self.x, self.y = WIDTH/2, 0
        self.speedx, self.speedy = BALL_SPEED, -BALL_SPEED
        self.move_ticker = MOVE_TICK
if __name__ == '__main__':
    main()
