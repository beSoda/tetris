import pygame
from config import *
from blocks import *
import random

LOCK_DELAY_TRIGGER = pygame.USEREVENT + 3


class tetris:
    def __init__(self):
        self.grid = grid()
        self.blocks = [IBlock(), JBlock(), LBlock(), OBlock(),
                       SBlock(), TBlock(), ZBlock()]
        self.current_block = self.get_random_block()
        self.next_block = self.get_random_block()
        self.game_over = False
        self.score = 0
        self.last_action_was_rotation = False

        self.b2b_streak = 0
        self.last_clear_was_difficult = False

        try:
            pygame.mixer.init()
            self.clear_sound = pygame.mixer.Sound("Sounds/clear.ogg")
            self.rotate_sound = pygame.mixer.Sound("Sounds/rotate.ogg")
            self.gameover_sound = pygame.mixer.Sound("Sounds/gameover.ogg")
            self.menu_sound = pygame.mixer.Sound("Sounds/menu.ogg")

        except pygame.error as e:
            print(f"Could not load sounds: {e}")
            # Placeholder functions to prevent crashes if sounds are missing
            self.clear_sound = lambda: None
            self.rotate_sound = lambda: None
            self.gameover_sound = lambda: None
            self.menu_sound = lambda: None

    def get_random_block(self):
        if len(self.blocks) == 0:
            self.blocks = [IBlock(), JBlock(), LBlock(), OBlock(),
                           SBlock(), TBlock(), ZBlock()]
        block = random.choice(self.blocks)
        self.blocks.remove(block)
        return block

    def update_score(self, lines_cleared, move_down_points):
        if lines_cleared == 1:
            self.score += 100
        elif lines_cleared == 2:
            self.score += 300
        elif lines_cleared == 3:
            self.score += 500
        self.score += move_down_points

    def main(self):
        while self.playing == True:
            self.events()
            self.update()
        self.running = False

    def move_left(self):
        self.current_block.move(0, -1)
        if self.block_inside() == False or self.block_fits() == False:
            self.current_block.move(0, 1)
        else:
            if not self.can_move_down():
                pygame.time.set_timer(LOCK_DELAY_TRIGGER, 500)

        self.last_action_was_rotation = False

    def move_right(self):
        self.current_block.move(0, 1)
        if self.block_inside() == False or self.block_fits() == False:
            self.current_block.move(0, -1)
        else:
            if not self.can_move_down():
                pygame.time.set_timer(LOCK_DELAY_TRIGGER, 500)

        self.last_action_was_rotation = False

    def move_down(self):
        if self.can_move_down():
            self.current_block.move(1, 0)
            pygame.time.set_timer(LOCK_DELAY_TRIGGER, 0)
        else:
            pygame.time.set_timer(LOCK_DELAY_TRIGGER, 500)

    def rotate_clockwise(self):
        if self.current_block.id == 4:
            return

        self.current_block.rotate()

        if self.block_inside() == False or self.block_fits() == False:
            self.current_block.undo_rotation()
            self.last_action_was_rotation = False
        else:
            self.rotate_sound.play()
            self.last_action_was_rotation = True

            if not self.can_move_down():
                pygame.time.set_timer(LOCK_DELAY_TRIGGER, 500)

    def rotate_counter_clockwise(self):
        if self.current_block.id == 4:
            return

        self.current_block.undo_rotation()

        if self.block_inside() == False or self.block_fits() == False:
            self.current_block.rotate()
            self.last_action_was_rotation = False
        else:
            self.rotate_sound.play()
            self.last_action_was_rotation = True

            if not self.can_move_down():
                pygame.time.set_timer(LOCK_DELAY_TRIGGER, 500)

    def rotate_180(self):
        if self.current_block.id == 4:
            return

        self.current_block.rotate_180()

        if self.block_inside() == False or self.block_fits() == False:
            self.current_block.undo_rotation_180()
            self.last_action_was_rotation = False
        else:
            self.rotate_sound.play()
            self.last_action_was_rotation = True

            if not self.can_move_down():
                pygame.time.set_timer(LOCK_DELAY_TRIGGER, 500)

    def hard_drop(self):
        drop_points = 0
        while True:
            self.current_block.move(1, 0)
            if self.block_inside() == False or self.block_fits() == False:
                self.current_block.move(-1, 0)
                self.lock_block()
                self.update_score(0, drop_points)
                break
            else:
                drop_points += 1

    def lock_block(self):
        tiles = self.current_block.get_cell_positions()
        for position in tiles:
            self.grid.grid[position.row][position.column] = self.current_block.id

        is_t_spin, is_mini = self.check_t_spin()
        self.last_action_was_rotation = False

        self.current_block = self.next_block
        self.next_block = self.get_random_block()
        rows_cleared = self.grid.clear_full_rows()

        # B2B
        current_clear_is_difficult = (rows_cleared == 4) or (
            is_t_spin and rows_cleared > 0)

        b2b_bonus = 0
        if current_clear_is_difficult and self.last_clear_was_difficult:
            self.b2b_streak += 1
            b2b_bonus = 1
        elif current_clear_is_difficult:
            self.b2b_streak = 1
        else:
            self.b2b_streak = 0

        self.last_clear_was_difficult = current_clear_is_difficult

        base_score = 0

        if is_t_spin and rows_cleared > 0:
            if rows_cleared == 1:
                base_score = 800
            elif rows_cleared == 2:
                base_score = 1200
            elif rows_cleared == 3:
                base_score = 1600

        elif rows_cleared == 4:
            base_score = 800

        elif rows_cleared > 0:
            if rows_cleared == 1:
                base_score = 100
            elif rows_cleared == 2:
                base_score = 300
            elif rows_cleared == 3:
                base_score = 500

        if b2b_bonus > 0:
            self.score += int(base_score * 1.5)
        else:
            self.score += base_score

        if rows_cleared > 0:
            self.clear_sound.play()

        if self.block_fits() == False:
            self.game_over = True
            self.gameover_sound.play()

    def can_move_down(self):
        self.current_block.move(1, 0)
        can_move = (self.block_inside() and self.block_fits())
        self.current_block.move(-1, 0)
        return can_move

    def lock_block_delayed(self):
        if self.can_move_down() == False:
            self.lock_block()

    def reset(self):
        self.grid.reset()
        self.blocks = [IBlock(), JBlock(), LBlock(), OBlock(),
                       SBlock(), TBlock(), ZBlock()]
        self.current_block = self.get_random_block()
        self.next_block = self.get_random_block()
        self.score = 0

    def block_fits(self):
        tiles = self.current_block.get_cell_positions()
        for tile in tiles:
            if self.grid.is_empty(tile.row, tile.column) == False:
                return False
        return True

    def check_t_spin(self):
        if self.current_block.id != 6:
            return False, 0

        if not self.last_action_was_rotation:
            return False, 0

        tiles = self.current_block.get_cell_positions()

        pivot_row = tiles[2].row
        pivot_col = tiles[2].column

        corners = [
            (pivot_row - 1, pivot_col - 1),
            (pivot_row - 1, pivot_col + 1),
            (pivot_row + 1, pivot_col - 1),
            (pivot_row + 1, pivot_col + 1)
        ]

        filled_corners = 0
        for r, c in corners:
            if not self.grid.is_inside(r, c) or not self.grid.is_empty(r, c):
                filled_corners += 1

        if filled_corners >= 3:
            return True, 1
        elif filled_corners == 2:
            return False, 0

        return False, 0

    def block_inside(self):
        tiles = self.current_block.get_cell_positions()
        for tile in tiles:
            if self.grid.is_inside(tile.row, tile.column) == False:
                return False
        return True

    def draw(self, screen):
        self.grid.draw(screen)
        self.current_block.draw(screen, 1, 1)

        if self.next_block.id == 3:
            self.next_block.draw(screen, 255, 290)
        elif self.next_block.id == 4:
            self.next_block.draw(screen, 255, 280)
        else:
            self.next_block.draw(screen, 270, 270)
