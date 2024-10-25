#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hid  # hidapi for joystick control
import time

class MyPad:
    def __init__(self):
        self.fps = 24
        self.result = 100

        # hidapiでジョイスティックの初期化 (Logitech RumblePadのVIDとPID)
        try:
            self.joystick = hid.device()
            self.joystick.open(0x046d, 0xc218)  # VID: 0x046d, PID: 0xc218 (example for Logitech)
            self.joystick.set_nonblocking(True)
            print("Joystickの名称: Logitech RumblePad 2 USB")
        except IOError:
            print("Joystickが見つかりませんでした。")

    def gamepadEvent(self):
        # 読み取りループのためのイベントチェック
        try:
            data = self.joystick.read(64)
            if data:
                hat_x, hat_y = data[0], data[1]  # Replace with actual report indices if different
                if hat_x == -1:
                    print("Le")
                    self.result = 1
                elif hat_x == 1:
                    print("Ri")
                    self.result = 2
                elif hat_y == 1:
                    print("St")
                    self.result = 3
                elif hat_y == -1:
                    print("Ba")
                    self.result = 4
                else:
                    self.result = 100
        except Exception as e:
            print(f"ジョイスティック入力エラー: {e}")

        return self.result

if __name__ == '__main__':
    mp = MyPad()

    while True:
        result = mp.gamepadEvent()
        time.sleep(1 / mp.fps)  # Adjust frame rate with sleep
