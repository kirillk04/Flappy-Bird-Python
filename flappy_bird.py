import pygame
from pygame.locals import *
import random

pygame.init()

#speed
clock = pygame.time.Clock()
fps = 60
ground_scroll = 0
scroll_speed = 4

#window settings
width = 600
screen_height = 800
screen = pygame.display.set_mode((width, screen_height))
pygame.display.set_caption('Flappy Bird')

#background
bg = pygame.image.load('sprites/bg.png')
ground_img = pygame.image.load('sprites/ground.png')

#variables
flying = False
game_over = False
pipe_gap = 180
pipe_frequency = 1500 #milliseconds
last_pipe = pygame.time.get_ticks() - pipe_frequency
score = 0
passed = False

#reset
button_img = pygame.image.load('sprites/restart.png')
def reset():
	pipe_group.empty()
	flappy.rect.x = 100
	flappy.rect.y = int(screen_height / 2)
	score = 0
	return score

#score
font = pygame.font.SysFont('Georgia', 55)
color = (255,255,255) #white
def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))

#classes
class Bird(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.images = []
		self.index = 0
		self.counter = 0
		for num in range(1, 4):
			img = pygame.image.load(f'sprites/bird{num}.png')
			self.images.append(img)
		self.image = self.images[self.index]
		self.rect = self.image.get_rect()
		self.rect.center = [x, y]
		self.speed = 0 #speed
		self.clicked = False

	def update(self):
		if flying == True:
			#gravity
			self.speed += 0.5
			if self.speed > 8:
				self.speed = 8
			if self.rect.bottom < 668:
				self.rect.y += int(self.speed)

		if game_over == False:
			#jump
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				self.clicked = True
				self.speed = -10
			if pygame.mouse.get_pressed()[0] == 0:
				self.clicked = False

			#animation
			self.counter += 1
			flap_cooldown = 5
			if self.counter > flap_cooldown:
				self.counter = 0
				self.index += 1
				if self.index >= len(self.images):
					self.index = 0
			self.image = self.images[self.index]
			
			#rotation
			self.image = pygame.transform.rotate(self.images[self.index], self.speed * -2)
		else:
			#death animation
			self.image = pygame.transform.rotate(self.images[self.index], -180)


class Pipe(pygame.sprite.Sprite):
	def __init__(self, x, y, position):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load('sprites/pipe.png')
		self.rect = self.image.get_rect()
		if position == 1: #top pipe
			self.image = pygame.transform.flip(self.image, False, True)
			self.rect.bottomleft = [x, y - int(pipe_gap / 2)]
		if position == -1: #bottom pipe
			self.rect.topleft = [x, y + int(pipe_gap / 2)] 

	def update(self):
		self.rect.x -= scroll_speed
		if self.rect.right < 0:
			self.kill() #gets rid of pipes offscreen so they dont lag the program


class Button():
	def __init__(self, x, y, image):
		self.image = image
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)

	def draw(self):
		action = False
		#get mouse position
		pos = pygame.mouse.get_pos()
		#check if mouse is over the button
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1:
				action = True

		#draw button
		screen.blit(self.image, (self.rect.x, self.rect.y))

		return action

#bird and pipe variables
bird_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()
flappy = Bird(100, int(screen_height / 2))
bird_group.add(flappy)

#reset button
button = Button(width // 2 - 70, screen_height // 2 - 50, button_img)

run = True #make sure exit works
while run:
	clock.tick(fps)
	
	#draw background
	screen.blit(bg, (0,-50))

	#bird and pipe animations
	bird_group.draw(screen)
	bird_group.update()
	pipe_group.draw(screen)

	#draw and scroll the ground
	screen.blit(ground_img, (ground_scroll, 668))

	#check the score
	if len(pipe_group) > 0:
		if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left\
			and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right\
			and passed == False: #checks that bird is in the middle of the pipe with left being inside pipe and right not passing pipe yet
			passed = True
		if passed == True:
			if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right: #fully passed pipes
				score += 1
				passed = False

	draw_text(str(score), font, color, int(width / 2), 20)

	#check if bird has hit the ground
	if flappy.rect.bottom > 668:
		game_over = True
		flying = False

	#look for collision
	if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:
		game_over = True

	if game_over == False and flying == True:
		#pipes
		time_now = pygame.time.get_ticks()
		if time_now - last_pipe > pipe_frequency: #frequency tracker
			pipe_height = random.randint(-100, 100)
			btm_pipe = Pipe(width, int(screen_height / 2) + pipe_height, -1)
			top_pipe = Pipe(width, int(screen_height / 2) + pipe_height, 1)
			pipe_group.add(btm_pipe)
			pipe_group.add(top_pipe)
			last_pipe = time_now

		pipe_group.update()
		
		#scroll the ground
		ground_scroll -= scroll_speed
		if abs(ground_scroll) > 35:
			ground_scroll = 0


	if game_over == True:
		if button.draw() == True: #checks that mouse is over the restart button and clicks
			game_over = False
			score = reset()

	for event in pygame.event.get():
		if event.type == pygame.QUIT: #quit
			run = False
		if event.type == pygame.MOUSEBUTTONDOWN and flying == False and game_over == False: #click to start game
			flying = True

	pygame.display.update()

pygame.quit()