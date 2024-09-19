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
            String, 
            queue_size=1
        )


        #==================================================

        # イニシャライズ

        #==================================================
        pygame.init()
        print("キーボード入力を使用します。")


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
def waitKeyboard(self, timeout=30):
    start_time = time.time()
    end_time = time.time()
    result = None
    while end_time - start_time <= timeout:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_UP, pygame.K_w]:
                    result = [1, 0, 0, 0]  # 上 or W
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    result = [0, 1, 0, 0]  # 下 or S
                elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                    result = [0, 0, 1, 0]  # 右 or D
                elif event.key in [pygame.K_LEFT, pygame.K_a]:
                    result = [0, 0, 0, 1]  # 左 or A
        if result is not None:
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
