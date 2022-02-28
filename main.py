import pygame , sys 
from random import choice


     #Enemy Class
class Enemy(pygame.sprite.Sprite):
    def __init__(self,x,y):
        super().__init__()
        self.image = pygame.image.load('graphics\Enemy.png')
        self.image = pygame.transform.scale(self.image, (45, 45))
        self.image = pygame.transform.flip(self.image,0,180)
        self.rect = self.image.get_rect(topleft = (x,y))
        self.value = 100

    def update(self,direction):
        self.rect.x += direction

     #Player Class
class Player(pygame.sprite.Sprite):
    def __init__(self,pos,constraint,speed):
        super().__init__()
        self.image = pygame.image.load('graphics\Spaceship.png')
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect(midbottom = pos)
        self.speed = speed
        self.max_x_contraint = constraint
        
        #cooldown for laser
        self.ready = True
        self.laser_time = 0
        self.laser_cooldown = 600
        self.lasers = pygame.sprite.Group()
        self.laser_sound = pygame.mixer.Sound('sound\shoot.wav')
        self.laser_sound.set_volume(0.2)

    #define keypress
    def get_input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        elif keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        
        if keys[pygame.K_SPACE] and self.ready:
            self.shoot_laser()
            self.ready = False
            self.laser_time = pygame.time.get_ticks()
            self.laser_sound.play()

    def recharge(self):
        if not self.ready:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_time >= self.laser_cooldown:
                self.ready = True

    #constrain obj inside the window
    def constraint(self):
        if self.rect.left <= 0:
            self.rect.left = 0
        if self.rect.right >= self.max_x_contraint:
            self.rect.right = self.max_x_contraint

    #calling laser
    def shoot_laser(self):
        self.lasers.add(Laser(self.rect.center , -8 ,self.rect.bottom))

    #update
    def update(self):
        self.get_input()
        self.constraint()
        self.recharge()
        self.lasers.update()

      #Laser Class
class Laser(pygame.sprite.Sprite):
    def __init__(self,pos,speed,screen_height):
        super().__init__()
        self.image = pygame.Surface((4,20)) #fixed resolution
        self.image.fill('white') #image color
        self.rect = self.image.get_rect(center = pos)
        self.speed = speed
        self.height_y_constraint = screen_height
    
    #destroy the laser when it is out of the window
    def destroy(self):
        if self.rext.y <= -50 or self.rect.y >= self.height_y_constraint +50:
            self.kill()
    #update
    def update(self):
        self.rect.y += self.speed

class Game:
    def __init__(self):
        
        #Player Setup
        player_sprite = Player ((screen_width / 2,screen_height),screen_width,5)
        self.player = pygame.sprite.GroupSingle(player_sprite)

        #Health  System
        self.lives = 3
        self.live_surf = pygame.image.load('graphics\Spaceship.png')
        self.live_surf = pygame.transform.scale(self.live_surf, (50, 50))
        self.live_x_start_pos = screen_width - (self.live_surf.get_size()[0] * 2 + 20)

        #Score System
        self.score = 0
        self.font = pygame.font.SysFont("Segoe UI", 35)

        #Enemy Setup
        self.enemies = pygame.sprite.Group()
        self.enemy_lasers = pygame.sprite.Group()
        self.enemy_setup(rows = 5 , cols = 8)
        self.enemy_direction = 1 #move enemies
        
        #Audio 
        music = pygame.mixer.Sound('sound\music.wav')
        music.set_volume(0.05)
        music.play(loops = -1)
        self.laser_sound = pygame.mixer.Sound('sound\shoot.wav')
        self.laser_sound.set_volume(0.1)
        self.explosion_sound = pygame.mixer.Sound('sound\invaderkilled.wav')
        self.explosion_sound.set_volume(0.1)    

    def enemy_setup(self,rows,cols,x_distance = 60 ,y_distance = 48, x_offset = 90 , y_offset = 20):
            for row_index, row in enumerate(range(rows)):
                for col_index,col in enumerate(range(cols)):
                    x = col_index * x_distance + x_offset
                    y = row_index * y_distance + y_offset
                    enemy_sprite = Enemy(x,y)
                    self.enemies.add(enemy_sprite)

    def enemy_position_check(self):
        all_enemies = self.enemies.sprites()
        for enemy in all_enemies:
            if enemy.rect.right >= screen_width:
                self.enemy_direction =-1
                self.enemy_move_down(2)
            elif enemy.rect.left <= 0 :
                self.enemy_direction = 1
                self.enemy_move_down(2)

    # enemies moving down
    def enemy_move_down(self,distance):
        if self.enemies:
            for enemy in self.enemies.sprites():
                enemy.rect.y += distance

    def enemy_shoot(self):
        if self.enemies.sprites():
            random_enemy = choice(self.enemies.sprites())#pick a random enemy
            laser_sprite = Laser(random_enemy.rect.center,6,screen_height)
            self.enemy_lasers.add(laser_sprite)
            self.laser_sound.play() #play laser sound when enemy shoots

    def collision_check(self):
        
        #player lasers
        if self.player.sprite.lasers:
            for laser in self.player.sprite.lasers:
                if pygame.sprite.spritecollide(laser,self.enemies,True):
                    laser.kill()
                    self.score += 100
                    self.explosion_sound.play()
        
        #enemy lasers
        if self.enemy_lasers:
            for laser in self.enemy_lasers:
                if pygame.sprite.spritecollide(laser,self.player,False):
                    laser.kill()
                    self.lives -= 1 
                                          
        #die if enemies colide with player
        if self.enemies:
            for enemy in self.enemies:
                if pygame.sprite.spritecollide(enemy,self.player,False):
                        self.lives -= 3

    # display remaining lives on upper right corner
    def display_lives(self):
        for live in range(self.lives - 1):
            x = self.live_x_start_pos + (live * (self.live_surf.get_size()[0] + 10))
            screen.blit(self.live_surf,(x,8))

    #display score
    def display_score(self):
        score_surf = self.font.render(f'score: {self.score}',False,'white')
        score_rect = score_surf.get_rect(topleft = (10,-10))
        screen.blit(score_surf , score_rect)

    #display You won! and close the game after 3 seconds,when all enemies are dead
    def victory_message(self):
        if not self.enemies.sprites():
            victory_surf = self.font.render('You won!',False,'white')
            victory_rect = victory_surf.get_rect(center = (screen_width / 2 , screen_height / 2))
            screen.blit(victory_surf , victory_rect)
            pygame.display.flip()
            pygame.time.delay(3000)
            pygame.quit()
            sys.exit()

    #display You lose! and close the game after 3 seconds,when you lose all your lives
    def defeat_message(self):
        if self.lives <=0:
            defeat_surf = self.font.render('You lose!',False,'white')
            defeat_rect = defeat_surf.get_rect(center = (screen_width / 2 , screen_height / 2))
            screen.blit(defeat_surf,defeat_rect)
            pygame.display.flip()
            pygame.time.delay(3000)
            pygame.quit()
            sys.exit()
            

    def run(self):

        self.player.update() #update movement
        self.enemies.update(self.enemy_direction) #update enemy movement
        self.enemy_position_check() #dont let enemies leave the window
        self.enemy_lasers.update() #enemy lasers

        self.collision_check() # collision

        self.player.sprite.lasers.draw(screen) #add laser on game

        self.player.draw(screen) #add player on game

        self.enemies.draw(screen) #add enemies on screen

        self.enemy_lasers.draw(screen) #add enemy lasers

        self.display_lives() #display lives
        self.display_score() #display score

        self.victory_message() #victory message
        self.defeat_message() #defeat message


#main
if __name__ == '__main__':
    pygame.init()
    screen_width = 600
    screen_height = 600
    screen = pygame.display.set_mode((screen_width,screen_height)) #display
    pygame.display.set_caption('Space Invaders')
    clock = pygame.time.Clock()
    game = Game()
    
    ENEMYLASER = pygame.USEREVENT + 1
    pygame.time.set_timer(ENEMYLASER,700) # 700ms laser enemies
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == ENEMYLASER:
                game.enemy_shoot()
            
        screen.fill((30,30,30)) #Gray background filter
        game.run()
        pygame.display.flip()
        clock.tick(60)
