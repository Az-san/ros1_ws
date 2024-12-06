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
            self.device = hid.device(0x046d, 0xc218)  # ロジクール RumblePad 2のVIDとPID
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
