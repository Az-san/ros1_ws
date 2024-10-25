#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#==================================================
## @file libraspi
## @author Kentaro NAKAMURA
## @modified for hidapi by Maiko Kudo
## @brief ライブラリクラス
#==================================================

#==================================================
# import
#==================================================
import sys
import roslib
import hid  # hidapiをインポート
import time
import math
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
#==================================================
class LibIF:
    #==================================================
    ## @fn __init__
    ## @brief コンストラクタ
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

        # hidapiを使ってゲームパッドに接続
        self.device = None
        try:
            self.device = hid.device()
            self.device.open(0x046d, 0xc218)# ロジクール RumblePad 2のVIDとPID
            print("ゲームパッドに接続しました: Logitech RumblePad 2 USB")
        except IOError as e:
            print(f"ゲームパッドが見つかりませんでした: {e}")

    #==================================================
    ## @fn delete
    ## @brief デストラクタ
    ## @param
    ## @return
    #==================================================
    def delete(self):
        if self.device:
            self.device.close()
        return

    #==================================================
    ## @fn waitGamepad
    ## @brief ゲームパッドの入力を待つ関数
    ## @param
    ## @return
    #==================================================
    def waitGamepad(self, timeout=30):
        start_time = time.time()
        result = None

        if not self.device:
            print("ゲームパッドが初期化されていません。")
            return result

        try:
            while time.time() - start_time <= timeout:
                report = self.device.read(8)  # 8バイトのデータを読み取る
                if report:
                    x, y = report[0], report[1]
                    if y == 1:
                        print("St")
                        result = [1, 0, 0, 0]
                    elif y == -1:
                        print("Ba")
                        result = [0, 1, 0, 0]
                    elif x == 1:
                        print("Ri")
                        result = [0, 0, 1, 0]
                    elif x == -1:
                        print("Le")
                        result = [0, 0, 0, 1]
                if result:
                    break
        except IOError as e:
            print(f"入力読み取りエラー: {e}")

        return result

    #==================================================
    ## @fn changeGamepadInputUDRLtoNSEW
    ## @brief ゲームパッドで入力したロボットの進行方向を上下左右から東西南北にする関数
    ## @param direction_udrl 決定されたロボットの進行方向（上下左右）
    ## @param rad 地図座標系におけるロボットの現在角度
    ## @return direction_nsew 決定されたロボットの進行方向（東西南北）
    #==================================================
    def changeGamepadInputUDRLtoNSEW(self, direction_udrl, rad):
        rad_list_udrl = [0.0, math.pi, math.pi * 3/2, math.pi/2]
        rad_direction_udrl = rad_list_udrl[[i for i in range(len(direction_udrl)) if direction_udrl[i] == 1][0]]
        direction_nsew = [0, 0, 0, 0]

        if 0.70 < math.cos(rad_direction_udrl + rad):
            direction_nsew[0] = 1
        elif -0.70 > math.cos(rad_direction_udrl + rad):
            direction_nsew[1] = 1
        elif -0.70 > math.sin(rad_direction_udrl + rad):
            direction_nsew[2] = 1
        elif 0.70 < math.sin(rad_direction_udrl + rad):
            direction_nsew[3] = 1

        return direction_nsew

    #==================================================
    ## @fn changeGUI
    ## @brief GUIの描画を変化させる関数
    ## @param state = "start"   スタート時のGUI
    ## @param state = "move"    ロボット移動時のGUI
    ## @param state = "wait"    ロボット周辺の地図作成を待っている時のGUI
    ## @param state = "select"  被験者の進行方向選択を待っている時のGUI
    ## @param state = "error"   被験者の選択した進行方向が進行不能である時のGUI
    ## @param state = x,y,rad   GUI上のロボットの位置情報を更新する際のデータ
    ## @return
    #==================================================
    def changeGUI(self, state="start"):
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
