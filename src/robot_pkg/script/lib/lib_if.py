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
import pygame
import math
import roslib
import rospy
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

        # pygameの初期化
        pygame.init()
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
        # 経過した時刻を取得
        end_time = time.time()
        # resultにキーボードの入力を格納 timeout秒でbreak
        result = None

        while end_time - start_time <= timeout:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w:  # Wキーで上方向
                        print("St")
                        result = [1, 0, 0, 0]
                    elif event.key == pygame.K_s:  # Sキーで下方向
                        print("Ba")
                        result = [0, 1, 0, 0]
                    elif event.key == pygame.K_d:  # Dキーで右方向
                        print("Ri")
                        result = [0, 0, 1, 0]
                    elif event.key == pygame.K_a:  # Aキーで左方向
                        print("Le")
                        result = [0, 0, 0, 1]
            
            if result is not None:
                break

            end_time = time.time()

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
            self.pub_gui_state.publish(",".join(state_str)) #座標値をコンマ区切りでPublish
