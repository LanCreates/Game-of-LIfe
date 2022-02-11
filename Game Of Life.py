import pygame as pg
import copy
import time
import random

from pygame.locals import (
    K_r,
    K_UP, K_DOWN,
    K_ESCAPE, K_SPACE,
    QUIT, KEYDOWN
)

pg.init()

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = tuple([x // 2 for x in WHITE])
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)

VERSION = "0.3"

class Animation:
    def vert_swipe(self, begin, end, screen_info):
        """Screen_info is a tuple of screen length, width, and unit used"""
        pass

class GameOfLife:
    _mult = 10 # One pixel = 10px
    _footer_sz = 80

    def __init__(self, size: tuple):
        self._length = ((size[0] if size[0] > 500 else False) or 500)
        self._width = ((size[1] if size[1] > 500 else False) or 500) + self._footer_sz
        self._state = {x: {y: 0 for y in range((self._width - self._footer_sz) // 10)} for x in range(self._length // 10)}

        # Window related
        self._SURFACE = pg.display.set_mode((self._length, self._width))
        pg.display.set_caption("Game Of Life")

    _speed = (0.025, 0.05, 0.1, 0.2)
    _speed_ptr = len(_speed) - 2

    @classmethod
    def alter_speed(cls, opt):
        if opt: cls._speed_ptr -= (1 if cls._speed_ptr != 0 else 0)
        else: cls._speed_ptr += (1 if cls._speed_ptr != len(cls._speed) else 0)
    
    def rand_seed(self):
        return tuple(((random.randint(0, len(self._state) - 1), 
                        random.randint(0, len(self._state[0]) - 1))) for _ in range(random.randint(0, 
                                                                        len(self._state[0])* len(self._state) - 1)))
    def get_seed(self):
        with open("game_seed.txt", 'r') as sd:
            text = sd.readlines()
            try:
                if text[0].strip() == "random":
                    return self.rand_seed()
                else:
                    # Getting delimiter
                    delimiter = ''.join([d for d in text[2] if not d.isnumeric()])
                    return tuple(map(lambda x: tuple(map(int, x.strip().split())), text[1:]))
            except IndexError:
                pass

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
                c_right = False if col == len(temp[row]) - 1 else True
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
            for col in self._state[row].keys():
                pixel = pg.Surface((self._mult, self._mult))
                pixel.fill({0: BLACK, 1: WHITE}[self._state[row][col]])
                self._SURFACE.blit(pixel, ((row)*self._mult, (col)*self._mult))

    _background = BLACK
    def clear(self):
        self._state = {x: {y: 0 for y in range((self._width - self._footer_sz) // 10)} for x in range(self._length // 10)}
        blank_scr = pg.Surface((self._length, self._width - self._footer_sz))
        blank_scr.fill(BLUE)#self._background)
        self._SURFACE.blit(blank_scr, (0, 0))
        pg.display.flip()

    def disp_border(self):
        BORDER = pg.Surface((self._length, (self._mult // 2)))
        BORDER.fill(GRAY)
        self._SURFACE.blit(BORDER, (0, self._width - self._footer_sz))
    
    TX16 = pg.font.Font("assets/guifont.ttf", 16)
    TX12 = pg.font.Font("assets/guifont.ttf", 12)
    
    def disp_speed(self):
        text = self.TX16.render(f"Speed {('4', '2', '1', '.5')[self._speed_ptr]:>2}x", True, WHITE, self._background)
        self._SURFACE.blit(text, (5, self._width - self._footer_sz + 10))

    def disp_version(self):
        text1 = self.TX12.render(f"{'version':>8}", True, WHITE, self._background)
        text2 = self.TX12.render(f"{VERSION:>8}", True, WHITE, self._background)
        self._SURFACE.blit(text1, (self._length - 6*self._mult,
                            self._width - 3*self._mult))
        self._SURFACE.blit(text2, (self._length - 6*self._mult,
                            self._width - 2*self._mult))

    IMG_0X = pg.image.load("assets/Stop.png")
    IMG_05X = pg.image.load("assets/Speed05x.png")
    IMG_1X = pg.image.load("assets/Speed1x.png")
    IMG_2X = pg.image.load("assets/Speed2x.png")
    IMG_4X = pg.image.load("assets/Speed4x.png")
    BLANK = pg.Surface((64, 64))
    BLANK.fill(_background)

    halted = True
    def disp_is_stopped(self):
        self._SURFACE.blit({True: self.IMG_0X, False: self.BLANK}[self.halted],
                (3*self._mult, self._width - self._footer_sz + 3*self._mult))

    def disp_speed_icons(self):
        self._SURFACE.blit(self.BLANK, (0, self._width - self._footer_sz + 3*self._mult))
        self._SURFACE.blit({3: self.IMG_05X, 2: self.IMG_1X, 1: self.IMG_2X, 0: self.IMG_4X}[self._speed_ptr],
                (0, self._width - self._footer_sz + 3*self._mult))

def main():
    # Initial
    running = True
    command = ''
    # Profile
    Game = GameOfLife((1000, 600))
    Game.disp_border()
    Game.disp_version()

    # Process
    seed = Game.get_seed()
    Game.plant_seed(seed)
    Game.render()
    pg.display.flip()
    time.sleep(Game._speed[Game._speed_ptr])
    
    # Game Loop
    while running:
        for event in pg.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                key = event.key
                if key == K_ESCAPE: running = False
                elif key == K_SPACE: Game.halted = {True: False, False: True}[Game.halted]
                elif key in (K_UP, K_DOWN): Game.alter_speed({K_UP: 1, K_DOWN: 0}[key])
            
            if Game.halted:
                if event.type == KEYDOWN:
                    key = event.key
                    if key == K_r: 
                        Game.clear()
                        Game.plant_seed(seed)
                        Game.render()

        if not Game.halted:
            Game.update()
            Game.render()
            time.sleep(Game._speed[Game._speed_ptr])

        Game.disp_speed_icons()
        Game.disp_is_stopped()
        Game.disp_speed()
        pg.display.flip()
    pg.quit()

main()
