
# Skier program
import pygame, sys, random
import configparser
cfg = configparser.ConfigParser()
cfg.read("srl.ini")
# different images for the skier depending on his direction
skier_images = ["skier_down.png", "skier_right1.png", "skier_right2.png",
                 "skier_left2.png", "skier_left1.png"]

# class for the Skier sprite
class SkierClass(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("skier_down.png")
        self.rect = self.image.get_rect()
        self.rect.center = [320, 100]
        self.angle = 0
        
    def turn(self, direction):
        global speed
        # load new image and change speed when the skier turns
        self.angle = self.angle + direction
        if self.angle < -2:  self.angle = -2
        if self.angle >  2:  self.angle =  2
        center = self.rect.center
        turnspeed = [0,2,15,-15,-2]
        self.image = pygame.image.load(skier_images[self.angle])
        self.rect = self.image.get_rect()
        self.rect.center = center
        speed = [turnspeed[self.angle], 6]
        return speed
    
    def move(self, speed):
        # move the skier right and left
        self.rect.centerx = self.rect.centerx + speed[0]
        if self.rect.centerx < 20:  self.rect.centerx = 20
        if self.rect.centerx > 620: self.rect.centerx = 620 
        
# class for obstacle sprites (trees and flags)
class ObstacleClass(pygame.sprite.Sprite):
    def __init__(self, image_file, location, type):
        pygame.sprite.Sprite.__init__(self) 
        self.image_file = image_file        
        self.image = pygame.image.load(image_file)
        self.rect = self.image.get_rect()
        self.rect.center = location
        self.type = type
        self.passed = False
                   
    def update(self):
        global speed
        self.rect.centery -= speed[1]*speedr*1.25
        if self.rect.centery < -32:
            self.kill()

# createS one "screen" of obstacles: 640 x 640
# use "blocks" of 64 x 64 pixels, so objects aren't too close together
def create_map():
    global obstacles
    biomes = {'flag':[['f','',''],['','',''],['','','']],
              'tree1':[['t','',''],['','t',''],['','','t']],
              'tree2':[['','','t'],['','t',''],['t','','']],
              'boundtree':[['t','','t'],['t','f','t'],['t','t','t']],
              'deepturn':[['f','t','t'],['f','f','f'],['t','t','f']]}
    imgfile = {"f":"flag","t":"tree"}
    locations = []
    obstas = cfg.get("userconfig", "diff")
    for i in range(int(obstas)//5+2):                 # 5 biomes per screen
        row = random.randint(0, 3)
        col = random.randint(0, 3)
        location  = [col * 192 + 32, row * 192 + 32 + 640] #center x, y for obstacle
        if not (location in locations):        # prevent 2 biomes in the same place
            locations.append(location)          
            biome = random.choice(list(biomes.keys()))
            for i in range(0,3):
                for j in range(0,3):
                    img = ""
                    if biomes[biome][i][j] == "t": img = "skier_tree.png"
                    elif biomes[biome][i][j] == "f":  img = "skier_flag.png"
                    else: continue
                    obstacle = ObstacleClass(img, [location[0]+j*64,location[1]+i*64], imgfile[biomes[biome][i][j]])
                    obstacles.add(obstacle)

# redraw the screen, including all sprites
def animate():
    screen.fill([230,230,230])
    obstacles.draw(screen)
    screen.blit(skier.image, skier.rect)
    screen.blit(score_text, [10, 10])
    #screen.blit(time_text, [240, 560])
    screen.blit(speedr_text, [10, 80])
    screen.blit(dist_text, [10, 530])
    screen.blit(fps, [560, 10])
    nc_chg = ft.render("N2O: "+str(nitro)+"%", 1, (0,0,0))
    screen.blit(nc_chg, [560, 600])
    pygame.display.flip()    

# initialize everything
pygame.init()
#background music
pygame.mixer.init()
pygame.mixer.music.load("bg_music.mp3")
pygame.mixer.music.set_volume(100)
pygame.mixer.music.play(-1)
screen = pygame.display.set_mode([640,640])
pygame.display.set_caption("Skier Release - Alvin can only play it", skier_images[0])
clock = pygame.time.Clock()
pygame.key.set_repeat(50,200)
speed = [0, 6]
obstacles = pygame.sprite.Group()   # group of obstacle objects
skier = SkierClass()
map_position = 0
points = 0
meter = 0
create_map()      # create one screen full of obstacles
font = pygame.font.Font(None, 40)
ft = pygame.font.Font(None, 20)
speedr = 1
accer = 0
f = [0, 4000, 7000, 10000, 12500]
x = 1
nitro = 100
timesince = 0
average = 0
times = 0
cfg_fps = int(cfg.get('advanced', 'fps'))
cfg_delay = float(cfg.get('advanced', 'delay'))
# main Pygame event loop
running = True
while running:
    average += speedr * 60
    times += 1
    clock.tick(cfg_fps)
    timesince += 1
    if timesince > 75:
        nitro += 1
        timesince = 0
    points += 10
    meter += speedr/3
    speedr += accer*random.random()
    fps_r = pygame.font.Font(None, 20)
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        
        if event.type == pygame.KEYDOWN:          # check for key presses
            if event.key == pygame.K_LEFT:        # left arrow turns left
                speed = skier.turn(-1)
            elif event.key == pygame.K_RIGHT:     #right arrow turns right
                speed = skier.turn(1)
            elif event.key == pygame.K_DOWN:
                skier.angle = 1
                skier.turn(-1)
                speed = [0, 6]
            elif event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_n:
                if nitro > 4:
                    nitro -= 5
                    accer = 0.01
    skier.move([speed[0], speed[1]*speedr*15.5])# move the skier (left or right)
    map_position += speed[1]                      # scroll the obstacles
    
    # create a new block of obstacles at the bottom
    if map_position >= 640:
        create_map()
        map_position = 0
    if nitro > 100:
        nitro = 100
    # check for hitting trees or getting flags
    hit =  pygame.sprite.spritecollide(skier, obstacles, False)
    if hit:
        if hit[0].type == "tree" and not hit[0].passed:
            #crashed into tree  
            points = points - 1000
            skier.image = pygame.image.load("skier_crash.png")  # crash image
            animate()  
            pygame.time.delay(1000)
            skier.image = pygame.image.load("skier_down.png")  # resume skiing
            skier.angle = 0
            speed = [0, 6]
            speedr = 1
            accer = 0
            hit[0].passed = True
        elif hit[0].type == "flag" and not hit[0].passed:   # got a flag
            points += 10
            accer += 0.005
            nitro += 5
            hit[0].kill()                                 # remove the flag 
    accer -= 0.0002
    if (speedr < 0.16):
        speedr = 0.16
    if (accer < -0.001):
        accer = -0.001
    obstacles.update()
    fps = fps_r.render("fps: "+str(clock.get_fps()), 1, (0, 0, 0))
    score_text = font.render("Score: " +str(points), 1, (0, 0, 0))
    speedr_text = font.render("Speed: " +str(int(speedr*60))
                              +"km/h, average: " + str(int(average/times)) + "km/h", 1, (0, 0, 0))
    dist_text = font.render(str(int(meter/1000.0*10)/10.0)+"km, "+str(int(meter))+"m", 1, (0, 0, 0))
    #time_text = ft.render(str(time), 1, (0,0,0))
    animate()
    pygame.time.delay(int(cfg_delay))
    
pygame.quit()
    
