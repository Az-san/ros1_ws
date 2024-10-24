#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygame
from pygame.locals import *
from PyQt4 import QtGui, QtCore
import sys


class MyPad():
    def __init__(self):
        self.fps = 24

        pygame.joystick.init()
        try:
            self.j = pygame.joystick.Joystick(0) # create a joystick instance
            self.j.init() # init instance
            print("Joystickの名称: " + self.j.get_name())
            print("ボタン数 : " + str(self.j.get_numbuttons()))
        except pygame.error:
            print("Joystickが見つかりませんでした。")

        # pygameの初期化
        pygame.init()

    def gamepadEvent(self):
        result = 100
        for event in pygame.event.get():
            if event.type == pygame.locals.JOYHATMOTION:
                x, y = self.j.get_hat(0)
                if x == -1:
                    print("Le")
                    result = 1
                elif x == 1:
                    print("Ri")
                    result = 2
                elif y == 1:
                    print("St")
                    result = 3
                elif y == -1:
                    print("Ba")
                    result = 4
        
        return result

if __name__ == '__main__':
    mp = MyPad()

    while True:
        result = mp.gamepadEvent()
