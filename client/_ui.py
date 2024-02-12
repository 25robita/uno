import pygame
from pygame.locals import *
import os

# Variables
BACKGROUND_COLOR = (255,255,255)
display = pygame.display # easy shortcut

# Init
pygame.init()
display.set_caption("hi")
display_surface = display.set_mode((0, 0))
display.toggle_fullscreen()
running = True

WIDTH, HEIGHT = display_surface.get_width(), display_surface.get_height()

blue_8 = pygame.image.load("./assets/Draw 4.svg")
blue_8 = pygame.transform.smoothscale(blue_8, (248*2, 380*2))

while running:
    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            running = False

    display_surface.fill(BACKGROUND_COLOR)
    display_surface.blit(blue_8, (0,0))
    display.update()
# Quit
pygame.quit()

os._exit(0)