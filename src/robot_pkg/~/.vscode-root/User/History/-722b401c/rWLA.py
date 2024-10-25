#!/usr/bin/env python3
# -*- coding: utf-8 -*-



#==================================================
## @file libraspi
## @author Kentaro NAKAMURA
## @brief ライブラリクラス
## @modified by Maiko Kudo
#==================================================




#==================================================
# import
#==================================================
import sys
import time
import math
import roslib
import rospy
import hid  # Import hidapi for HID keyboard handling
from std_msgs.msg import String

sys.path.append(roslib.packages.get_pkg_dir("robot_pkg") + "/script/import")
from common_import import *

#==================================================

# グローバル

#==================================================



#==================================================
## @class LibIF
## @brief 自作ライブラリクラス
## @modified by Maiko Kudo
#==================================================
class LibIF:
    #==================================================
    ## @fn __init__
    ## @brief コンストラクタ
    ## @modified by Maiko Kudo
    ## @param 
    ## @return
    #==================================================
    def __init__(self):
        # メンバ変数
        self.pub_gui_state = rospy.Publisher(
            'gui_state', 
            String, 
            queue_size=1
        )

        # HID Device Initialization for Keyboard Input
        self.keyboard = hid.device()
        self.keyboard.open(0x046d, 0xc31c)  # Replace with your keyboard's VID and PID
        self.keyboard.set_nonblocking(True)
        print("キーボード操作が有効です。")

    #==================================================
    ## @fn waitKeyboard
    ## @brief キーボードの入力を待つ関数
    ## @modified by Maiko Kudo
    ## @param
    ## @return
    #==================================================
    def waitKeyboard(self, timeout=30):
        # 開始の時刻を保存
        start_time = time.time()
        result = None

        while time.time() - start_time <= timeout:
            data = self.keyboard.read(8)  # Adjust report length if needed
            if data:
                key_code = data[2]  # Typically the key code is in index 2; adjust as necessary
                
                if key_code == 0x1A:  # 'W' key
                    print("St")
                    result = [1, 0, 0, 0]
                elif key_code == 0x16:  # 'S' key
                    print("Ba")
                    result = [0, 1, 0, 0]
                elif key_code == 0x20:  # 'D' key
                    print("Ri")
                    result = [0, 0, 1, 0]
                elif key_code == 0x04:  # 'A' key
                    print("Le")
                    result = [0, 0, 0, 1]
                
                if result is not None:
                    break

        return result
    

    #==================================================
    ## @fn changeKeyboardInputUDRLtoNSEW
    ## @brief キーボードで入力したロボットの進行方向を上下左右から東西南北にする関数
    ## @modified by Maiko Kudo
    ## @param direction_udrl 決定されたロボットの進行方向（上下左右）
    ## @param rad 地図座標系におけるロボットの現在角度
    ## @return direction_nsew 決定されたロボットの進行方向（東西南北）
    #==================================================
    def changeKeyboardInputUDRLtoNSEW(self, direction_udrl, rad):
        # 上下左右にロボット座標系の角度を割り振る
        rad_list_udrl = [0.0, math.pi, math.pi*3/2, math.pi/2]
        rad_direction_udrl = rad_list_udrl[[i for i in range(len(direction_udrl)) if direction_udrl[i] == 1][0]]

        # 地図座標系におけるロボット座標系の角度を求め、決定されたロボットの進行方向（東西南北）を求める
        direction_nsew = [0, 0, 0, 0]
        if 0.70 < math.cos(rad_direction_udrl + rad):      # 決定されたロボットの進行方向が 北
            direction_nsew[0] = 1
        elif -0.70 > math.cos(rad_direction_udrl + rad):   # 決定されたロボットの進行方向が 南
            direction_nsew[1] = 1
        elif -0.70 > math.sin(rad_direction_udrl + rad):   # 決定されたロボットの進行方向が 東
            direction_nsew[2] = 1
        elif 0.70 < math.sin(rad_direction_udrl + rad):    # 決定されたロボットの進行方向が 西
            direction_nsew[3] = 1

        return direction_nsew
    
    
    #==================================================
    ## @fn changeGUI
    ## @brief GUIの描画を変化させる関数
    ## @param state = "start"   スタート時のGUI
    ## @param state = "move"    ロボット移動時のGUI
    ## @param state = "wait"    ロボット周辺の地図作成を待っている時のGUI
    ## @param state = "select"   被験者の進行方向選択を待っている時のGUI
    ## @param state = "error"   被験者の選択した進行方向が進行不能である時のGUI
    ## @param state = x,y,rad   GUI上のロボットの位置情報を更新する際のデータ
    ## @return
    #==================================================
    def changeGUI(
        self,
        state = "start"
    ):
        if state == "start":
            self.pub_gui_state.publish("start")
        elif state == "move":
            self.pub_gui_state.publish("move")
        elif state == "wait":
            self.pub_gui_state.publish("wait")
        elif state == "select":
            self.pub_gui_state.publish("select")
        elif state == "error":
            self.pub_gui_state.publish("error")
        else:
            state_str = [str(n) for n in state]
            self.pub_gui_state.publish(",".join(state_str))  # 座標値をコンマ区切りでPublish
