import pygame as pg
import copy
import time
import random

from pygame.locals import (
    K_UP, K_DOWN,
    K_ESCAPE, K_SPACE,
    QUIT, KEYDOWN
)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)

class GameOfLife:
    _speed_ptr = 1
    _speed = (0, 0.1, 0.5)
    _mult = 10 # One pixel = 10px
    _footer_sz = 50

    def __init__(self, size: tuple):
        self._length = ((size[0] if size[0] > 500 else False) or 500)
        self._width = ((size[1] if size[1] > 500 else False) or 500) + self._footer_sz
        self._state = {x: {y: 0 for y in range((self._width - self._footer_sz) // 10)} for x in range((self._length) // 10)}

        # Window related
        self._surface = pg.display.set_mode((self._length, self._width))
        pg.display.set_caption("Game Of Life")

    def border(self):
        _border = pg.Surface((self._mult, self._mult))
        _border.fill(BLUE)
        self._surface.blit(_border, ((((self._length - self._footer_sz) // 10)*self._mult,
                                      ((self._width - self._footer_sz) // 10 + 10)*self._mult)))

    @classmethod
    def alter_speed(cls, opt):
        if opt: cls._speed_ptr += (1 if cls._speed_ptr != 2 else 0)
        else: cls._speed_ptr -= (1 if cls._speed_ptr != 0 else 0)
    
    def rand_seed(self):
        return (((random.randint(0, len(self._state) - 1), 
                random.randint(0, len(self._state[0]) - 1))) for _ in range(random.randint(0, 
                                                                        len(self._state[0])* len(self._state) - 1)))

    def plant_seed(self, seed):
        for pos in seed:
            self._state[pos[0]][pos[1]] = 1

    def update(self):
        temp = copy.deepcopy(self._state)
        for row in temp.keys():
            c_up = False if row == 0 else True
            c_down = False if row == len(self._state) - 1 else True
            for col in temp[row].keys():
                neighbors = 0
                c_left = False if col == 0 else True
                c_right = False if col == len(self._state[0]) - 1 else True
                
                if c_up:
                    neighbors += temp[row - 1][col]
                    if c_right: neighbors += temp[row - 1][col + 1]
                    if c_left: neighbors += temp[row - 1][col - 1]
                if c_down:
                    neighbors += temp[row + 1][col]
                    if c_right: neighbors += temp[row + 1][col + 1]
                    if c_left: neighbors += temp[row + 1][col - 1]
                if c_right: neighbors += temp[row][col + 1]
                if c_left: neighbors += temp[row][col - 1]
                # Conclude
                if temp[row][col] == 0:
                    if neighbors == 3:
                        self._state[row][col] = 1
                else:
                    if neighbors < 2 or neighbors > 3:
                        self._state[row][col] = 0
                    
    def render(self):
        for row in self._state.keys():
            for col in self._state.keys():
                pixel = pg.Surface((self._mult, self._mult))
                pixel.fill({0: BLACK, 1: WHITE}[self._state[row][col]])
                self._surface.blit(pixel, ((row)*self._mult, (col)*self._mult))

    def reset(self):
        self._state = {x: {y: 0 for y in range(self._width)} for x in range(self._length)}
        self.render()

def main():
    # Initial
    halted = True
    running = True
    pg.init()
    # Profile
    Game = GameOfLife((500, 500))
    seed = tuple([(x, x) for x in range(len(Game._state))] + 
                 [(x, len(Game._state) - 1 - x) for x in range(len(Game._state))] +
                 [((len(Game._state) - 1) // 2, y) for y in range(len(Game._state[0]))] + 
                 [(x, (len(Game._state) - 1) // 2) for x in range(len(Game._state))])

    # Process
    Game.plant_seed(seed)
    Game.render()
    pg.display.flip()
    time.sleep(Game._speed[Game._speed_ptr])
    while running:
        for event in pg.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                key = event.key

                # Only one key at a time
                if key == K_ESCAPE: running = False
                elif key == K_SPACE: halted = {True: False, False: True}[halted]
                elif key in (K_UP, K_DOWN): Game.alter_speed({K_UP: 1, K_DOWN: 0}[key])

        if not halted:
            Game.update()
            Game.render()
            time.sleep(Game._speed[Game._speed_ptr])
        pg.display.flip()
    pg.quit()

main()
