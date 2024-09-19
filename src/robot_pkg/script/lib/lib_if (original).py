#!/usr/bin/env python3
# -*- coding: utf-8 -*-




#==================================================

## @file libraspi
## @author Kentaro NAKAMURA
## @brief ライブラリクラス

#==================================================




#==================================================

# import

#==================================================
import sys
import roslib

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
    def __init__(
        self
    ):
        #==================================================

        # メンバ変数

        #==================================================

        #==================================================

        # ROSインタフェース

        #==================================================
        self.pub_gui_state = rospy.Publisher(
            'gui_state', 
            Int16, 
            queue_size=1
        )


        #==================================================

        # イニシャライズ

        #==================================================
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


        return




    #==================================================
    
    ## @fn delete
    ## @brief デストラクタ
    ## @param
    ## @return

    #==================================================
    def delete(
        self
    ):
        #==================================================

        # ファイナライズ

        #==================================================


        return



    #==================================================
    
    ## @fn waitGamepad
    ## @brief ゲームパッドの入力を待つ関数
    ## @param
    ## @return

    #==================================================
    def waitGamepad(
        self,
        timeout = 30
    ):
        # 開始の時刻を保存
        start_time = time.time()
        # 経過した時刻を取得
        end_time = time.time()

        # resultにゲームパッドの値を格納 timeout秒でbreak
        result = None
        while end_time - start_time <= timeout:
            for event in pygame.event.get():
                if event.type == pygame.locals.JOYHATMOTION:
                    x, y = self.j.get_hat(0)
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

            if result != None:

                break

            end_time = time.time()

        return result


    #==================================================
    
    ## @fn changeGamepadInputUDRLtoNSEW
    ## @brief ゲームパッドで入力したロボットの進行方向を上下左右から東西南北にする関数
    ## @param direction_udrl 決定されたロボットの進行方向（上下左右）
    ## @param rad 地図座標系におけるロボットの現在角度
    ## @return direction_nsew 決定されたロボットの進行方向（東西南北）

    #==================================================
    def changeGamepadInputUDRLtoNSEW(
        self,
        direction_udrl,
        rad
    ):
        # 上下左右にロボット座標系の角度を割り振る
        rad_list_udrl = [0.0, math.pi, math.pi*3/2, math.pi/2]
        rad_direction_udrl = rad_list_udrl[[i for i in range(len(direction_udrl)) if direction_udrl[i]==1][0]]

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
    ## @param state = "judge"   被験者の進行方向選択を待っている時のGUI
    ## @param state = "error"   被験者の選択した進行方向が進行不能である時のGUI
    ## @return

    #==================================================
    def changeGUI(
        self,
        state = "start"
    ):
        if state == "start":
            self.pub_gui_state.publish(0)
        elif state == "move":
            self.pub_gui_state.publish(1)
        elif state == "wait":
            self.pub_gui_state.publish(2)
        elif state == "judge":
            self.pub_gui_state.publish(3)
        elif state == "error":
            self.pub_gui_state.publish(4)
