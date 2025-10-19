import pygame
from config import *
from blocks import *
import sys
from tetris import tetris


pygame.init()

try:
    pygame.mixer.init()
    music_file = pygame.mixer.Sound("Sounds/menu.ogg")
    pygame.mixer.music.load(music_file)
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.5)

except pygame.error as e:
    print(f"Warning: Could not load or play music file: {e}")

title_font = pygame.font.Font(None, 40)
score_surface = title_font.render("Score", True, Colors.WHITE)
next_surface = title_font.render("Next", True, Colors.WHITE)
game_over_surface = title_font.render("GAME OVER", True, Colors.WHITE)

score_rect = pygame.Rect(320, 55, 170, 60)
next_rect = pygame.Rect(320, 215, 170, 180)

screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Tetris")

clock = pygame.time.Clock()

Tetris = tetris()

GAME_UPDATE = pygame.USEREVENT
pygame.time.set_timer(GAME_UPDATE, 200)

DAS_TRIGGER = pygame.USEREVENT + 1
DAS_REPEAT = pygame.USEREVENT + 2
LOCK_DELAY_TRIGGER = pygame.USEREVENT + 3

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if Tetris.game_over == False:
            if event.type == pygame.KEYDOWN:
                pygame.time.set_timer(DAS_TRIGGER, 0)
                pygame.time.set_timer(DAS_REPEAT, 0)

                if event.key == pygame.K_LEFT:
                    Tetris.move_left()
                    pygame.time.set_timer(DAS_TRIGGER, 117)
                elif event.key == pygame.K_RIGHT:
                    Tetris.move_right()
                    pygame.time.set_timer(DAS_TRIGGER, 117)
                elif event.key == pygame.K_DOWN:
                    Tetris.move_down()
                    Tetris.update_score(0, 1)
                    pygame.time.set_timer(DAS_REPEAT, 17)
                elif event.key == pygame.K_UP:
                    Tetris.rotate_180()
                elif event.key == pygame.K_d:
                    Tetris.rotate_clockwise()
                elif event.key == pygame.K_s:
                    Tetris.rotate_counter_clockwise()
                elif event.key == pygame.K_SPACE:
                    Tetris.hard_drop()

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT or event.key == pygame.K_DOWN:
                    pygame.time.set_timer(DAS_TRIGGER, 0)
                    pygame.time.set_timer(DAS_REPEAT, 0)

            elif event.type == DAS_TRIGGER:
                pygame.time.set_timer(DAS_TRIGGER, 0)

                keys = pygame.key.get_pressed()
                if keys[pygame.K_LEFT]:
                    pygame.time.set_timer(DAS_REPEAT, 17)
                elif keys[pygame.K_RIGHT]:
                    pygame.time.set_timer(DAS_REPEAT, 17)

            elif event.type == DAS_REPEAT:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_LEFT]:
                    Tetris.move_left()
                elif keys[pygame.K_RIGHT]:
                    Tetris.move_right()
                elif keys[pygame.K_DOWN]:
                    Tetris.move_down()
                    Tetris.update_score(0, 1)
            elif event.type == LOCK_DELAY_TRIGGER:
                pygame.time.set_timer(LOCK_DELAY_TRIGGER, 0)

                if Tetris.can_move_down() == False:
                    Tetris.lock_block_delayed()

        if event.type == pygame.KEYDOWN and Tetris.game_over == True:
            Tetris.game_over = False
            Tetris.reset()
            pygame.time.set_timer(DAS_TRIGGER, 0)
            pygame.time.set_timer(DAS_REPEAT, 0)

        if event.type == GAME_UPDATE and Tetris.game_over == False:
            Tetris.move_down()
    # Drawing
    score_value_surface = title_font.render(
        str(Tetris.score), True, Colors.WHITE)

    screen.fill(Colors.GREY)
    screen.blit(score_surface, (365, 20, 50, 50))
    screen.blit(next_surface, (375, 180, 50, 50))

    if Tetris.game_over == True:
        screen.blit(game_over_surface, (320, 450, 50, 50))

    pygame.draw.rect(screen, Colors.LIGHT_PURPLE, score_rect, 0, 10)
    screen.blit(score_value_surface, score_value_surface.get_rect(centerx=score_rect.centerx,
                                                                  centery=score_rect.centery))
    pygame.draw.rect(screen, Colors.LIGHT_PURPLE, next_rect, 0, 10)
    Tetris.draw(screen)

    pygame.display.update()
    clock.tick(60)
