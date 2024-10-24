#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#==================================================
## @file sm_main.py
## @original author Kentaro NAKAMURA
## @author Takumi FUJI
## @brief メインステートマシン
#==================================================


#==================================================
# import
#==================================================
import sys
import roslib
import rospy
import os

import smach
#import smach_ros

sys.path.append(roslib.packages.get_pkg_dir("robot_pkg") + "/script/import")
from common_import import *

#==================================================
# グローバル
#==================================================
CheckIntersectionCLOCK = 0.5


#==================================================
## @class Init
## @berif 初期化ステート
#==================================================
class Init(
    smach.State
):
    #==================================================
    ## @fn __init__
    ## @brief コンストラクタ
    ## @param lib ライブラリ群
    ## @return
    #==================================================
    def __init__(
        self,
        lib = {}
    ):
        #==================================================
        # イニシャライズ
        #==================================================
        smach.State.__init__(
            self,
            outcomes = ["next", "except"]
        )

        self._lib = lib

        return




    #==================================================
    ## @fn __del__
    ## @brief デストラクタ
    ## @param
    ## @return
    #==================================================
    def __del__(self):
        #==================================================
        # ファイナライズ
        #==================================================

        return




    #==================================================
    ## @fn execute
    ## @brief 実行関数
    ## @param userdata
    ## @return
    #==================================================
    def execute(
        self,
        userdata
    ):
        
        return "next"




#==================================================
## @class Wait4Start
## @berif 開始待ちステート
#==================================================
class Wait4Start(
    smach.State
):
    #==================================================
    ## @fn __init__
    ## @brief コンストラクタ
    ## @param lib ライブラリ郡
    ## @return
    #==================================================
    def __init__(
        self,
        lib = {}
    ):
        #==================================================
        # イニシャライズ
        #==================================================
        smach.State.__init__(
            self,
            outcomes = ["next", "except"]
        )

        self._lib = lib

        return




    #==================================================
    ## @fn __del__
    ## @brief デストラクタ
    ## @param
    ## @return
    #==================================================
    def __del__(self):
        #==================================================
        # ファイナライズ
        #==================================================

        return




    #==================================================
    ## @fn execute
    ## @brief 実行関数
    ## @param userdata
    ## @return
    #==================================================
    def execute(
        self,
        userdata
    ):

        input("Enter to START >>> ")

        return "next"




#==================================================
## @class Start
## @brief 開始ステート
#==================================================
class Start(
    smach.State
):
    #==================================================
    ## @fn __init__
    ## @brief コンストラクタ
    ## @param lib ライブラリ群
    ## @return
    #==================================================
    def __init__(
        self,
        lib = {}
    ):
        #==================================================
        # イニシャライズ
        #==================================================
        smach.State.__init__(
            self,
            outcomes = ["next", "except"]
        )

        self._lib = lib

        return



    #==================================================
    ## @fn __del__
    ## @brief デストラクタ
    ## @param
    ## @return
    #==================================================
    def __del__(self):
        #==================================================
        # ファイナライズ
        #==================================================

        return




    #==================================================
    ## @fn execute
    ## @brief 実行関数
    ## @param userdata
    ## @return
    #==================================================
    def execute(
        self,
        userdata
    ):
        
        return "next"



#==================================================
## @class StartTrial
## @berif 
#==================================================
class StartTrial(
    smach.State
):
    #==================================================
    ## @fn __init__
    ## @brief コンストラクタ
    ## @param lib ライブラリ郡
    ## @return
    #==================================================
    def __init__(
        self,
        lib = {}
    ):
        #==================================================
        # イニシャライズ
        #==================================================
        smach.State.__init__(
            self,
            outcomes = ["next", "restart", "loop", "except"]
        )

        self._lib = lib


        #==================================================
        # ROSインタフェース
        #==================================================


        return




    #==================================================
    ## @fn __del__
    ## @brief デストラクタ
    ## @param
    ## @return
    #==================================================
    def __del__(self):
        #==================================================
        # ファイナライズ
        #==================================================

        return



    #==================================================
    ## @fn execute
    ## @brief 実行関数
    ## @param 
    ## @return
    #==================================================
    def execute(
        self,
        userdata
    ):

        exp_cnt = self._lib["record"].getExpCnt()

        self._lib["record"].initPath(rospy.get_param("/exp_type", "")) # データ保存先の初期化

        rospy.set_param(rospy.get_name() + "/inf_rad_sorted", [])
        rospy.set_param(rospy.get_name() + "/position_meter", [])
        rospy.set_param(rospy.get_name() + "/nearest_inf_rad_to_present_rad", 0.0)
        rospy.set_param(rospy.get_name() + "/direction_candidates_inf_rad_sorted_idx", [-1,-1,-1,-1])
        rospy.set_param(rospy.get_name() + "/robot_decided_direction", [])
        rospy.set_param(rospy.get_name() + "/human_decided_direction", [])
        rospy.set_param(rospy.get_name() + "/pilot", [])
        rospy.set_param(rospy.get_name() + "/decided_direction", [])
        rospy.set_param(rospy.get_name() + "/decided_direction_inf_rad_sorted", 0)
        rospy.set_param(rospy.get_name() + "/nearest_x_table_idx", -1)
        rospy.set_param(rospy.get_name() + "/errp", 0)
        rospy.set_param(rospy.get_name() + "/unexp_points_meter", [])

        # ２試行目以降は、記録したQとXを使用する
        #elif rospy.get_param("/exp_type", "") == "ee":
        print("###    EEG  experiment    ###")
        if rospy.get_param("/data_file", "") == "":
            rospy.set_param(rospy.get_name() + "/q_table", [])
            rospy.set_param(rospy.get_name() + "/x_table", [])
        else:
            save_date_path = roslib.packages.get_pkg_dir("robot_pkg") + "/data" + "/" + rospy.get_param("/data_file", "")
            q_table = self._lib["record"].loadRecordQTable(save_date_path)
            x_table = self._lib["record"].loadRecordXTable(save_date_path)
            rospy.set_param(rospy.get_name() + "/q_table", q_table)
            rospy.set_param(rospy.get_name() + "/x_table", x_table)

        # be時であれば、ストップウォッチを開始する
        #if rospy.get_param("/exp_type", "") == "be":
        self._lib["record"].recordTime(state="start")

        # GUIの変更
        self._lib["if"].changeGUI("start")

        return "next"





#==================================================
## @class CheckIntersection
## @brief 
#==================================================
class CheckIntersection(
    smach.State
):
    #==================================================
    ## @fn __init__
    ## @brief コンストラクタ
    ## @param lib ライブラリ群
    ## @return
    #==================================================
    def __init__(
        self,
        lib = {}
    ):
        #==================================================
        # イニシャライズ
        #==================================================
        smach.State.__init__(
            self,
            outcomes = ["true", "false", "loop", "except"]
        )

        self._lib = lib


        #==================================================
        # ROSインタフェース
        #==================================================

        return



    #==================================================
    ## @fn __del__
    ## @brief デストラクタ
    ## @param
    ## @return
    #==================================================
    def __del__(self):
        #==================================================
        # ファイナライズ
        #==================================================

        return



    #==================================================
    ## @fn execute
    ## @brief 実行関数
    ## @param 
    ## @return
    #==================================================
    def execute(
        self,
        userdata
    ):
        inf_rad_sorted = self._lib["scan"].getLaserInfRad()
        position_meter = self._lib["map"].getRobotPointMeter()

        rospy.set_param(rospy.get_name() + "/inf_rad_sorted", inf_rad_sorted)

        # GUIの変更
        self._lib["if"].changeGUI("move")

        # 進行可能な空間がない場合
        if len(inf_rad_sorted) == 0:
            rospy.loginfo("no passible way !!!(ChkInterS)")

            rospy.sleep(CheckIntersectionCLOCK)

            # かつ、ロボットが動いていない時は回避行動を行う（アドホック）
            robot_vel = self._lib["nav"].getRobotVel()
            if robot_vel < 0.001:
                rospy.loginfo("escaping now ...(ChkInterS)")

                # ロボットを180deg回転させる
                self._lib["nav"].sendRotationTwist(position_meter[2] - math.pi, position_meter[2])
                # とにかく前進する
                self._lib["nav"].sendRunTwist(
                    position_meter[2],
                    position_meter[2],
                    rad_speed = 0.0
                )

            return "loop"

        # 交差点を見つけた場合
        elif 2 < len(inf_rad_sorted):
            rospy.loginfo("Intersection found.")

            # ロボットを停止させる
            self._lib["nav"].sendRunTwist(
                inf_rad_sorted[0],
                position_meter[2],
                lin_speed = 0,
                rad_speed = 0
            )

            rospy.sleep(1.0)

            # 未探索領域の座標を求める
            inf_rad_sorted = self._lib["scan"].getLaserInfRad()
            resolution = self._lib["map"].getResolution()
            point_pixel = self._lib["map"].getRobotPointPixel()
            inf_points_pixel = self._lib["scan"].getLaserInfPointPixel(inf_rad_sorted, point_pixel[0], point_pixel[1], resolution)
            map_out = self._lib["map"].getMap()
            unexp_points_pixel, unexp_rad_sorted = self._lib["map"].searchUnexpAroundPointPixel(map_out, inf_points_pixel, inf_rad_sorted)
            unexp_points_meter = self._lib["map"].convPixels2Meters(unexp_points_pixel)
            if len(unexp_points_pixel) != 0:
                for i in range(len(unexp_points_meter)):
                    print("unexp_points_meter = {}, {}".format(unexp_points_meter[i][0], unexp_points_meter[i][1]))

            rospy.set_param(rospy.get_name() + "/unexp_points_meter", unexp_points_meter)

            return "true"

        # 進行可能な空間がある場合(交差点ではない場合)
        else:
            #rospy.loginfo("I will go straight.")

            return "false"




#==================================================
## @class GoAhead
## @berif 
#==================================================
class GoAhead(
    smach.State
):
    #==================================================
    ## @fn __init__
    ## @brief コンストラクタ
    ## @param lib ライブラリ郡
    ## @return
    #==================================================
    def __init__(
        self,
        lib = {}
    ):
        #==================================================
        # イニシャライズ
        #==================================================
        smach.State.__init__(
            self,
            outcomes = ["next", "loop", "reset", "except"]
        )

        self._lib = lib

        #==================================================
        # ROSインタフェース
        #==================================================

        return




    #==================================================
    ## @fn __del__
    ## @brief デストラクタ
    ## @param
    ## @return
    #==================================================
    def __del__(self):
        #==================================================
        # ファイナライズ
        #==================================================

        return



    #==================================================
    ## @fn execute
    ## @brief 実行関数
    ## @param 
    ## @return
    #==================================================
    def execute(
        self,
        userdata
    ):
        inf_rad_sorted = rospy.get_param(rospy.get_name() + "/inf_rad_sorted", [])

        position_meter = self._lib["map"].getRobotPointMeter()

        # 手前に壁がある場合、
        if self._lib["scan"].getAheadDistance() < 1.0:
            # ロボットを停止させる
            self._lib["nav"].sendRunTwist(
                inf_rad_sorted[0],
                position_meter[2],
                lin_speed = 0,
                rad_speed = 0
            )

            rospy.sleep(1.0)

            # 現在のロボットの前進方向から一番近いinf_radを発見する
            nearest_inf_rad_to_present_rad = inf_rad_sorted[0]
            for i in range(len(inf_rad_sorted)):
                if math.cos(inf_rad_sorted[i] - position_meter[2]) >= math.cos(nearest_inf_rad_to_present_rad - position_meter[2]):
                    nearest_inf_rad_to_present_rad = inf_rad_sorted[i]
            # ロボットを回転させる（位置調整のため）
            self._lib["nav"].sendRotationTwist(nearest_inf_rad_to_present_rad, position_meter[2])
            rospy.sleep(1.0)

        else:
            
            # 現在のロボットの前進方向から一番近いinf_radを発見する
            nearest_inf_rad_to_present_rad = inf_rad_sorted[0]
            for i in range(len(inf_rad_sorted)):
                if math.cos(inf_rad_sorted[i] - position_meter[2]) >= math.cos(nearest_inf_rad_to_present_rad - position_meter[2]):
                    nearest_inf_rad_to_present_rad = inf_rad_sorted[i]
            # nearest_inf_rad_to_present_rad方向に前進する
            self._lib["nav"].sendRunTwist(
                nearest_inf_rad_to_present_rad,
                position_meter[2],
            )

            rospy.sleep(CheckIntersectionCLOCK)

            # ロボットが動いていない場合、トライアルをリセットする
            robot_vel = self._lib["nav"].getRobotVel()
            if robot_vel < 0.001:
                rospy.loginfo("escaping now ...(GoAhead)")
                self._lib["record"].recordGoal(False)
                self._lib["record"].recordStatus("stack")
                self._lib["record"].recordTime(state="stop")
                self._lib["nav"].resetTrial()

                return "reset"
                

        return "next"



#==================================================
## @class MakeDirectionCandidates
## @berif 
#==================================================
class MakeDirectionCandidates(
    smach.State
):
    #==================================================
    ## @fn __init__
    ## @brief コンストラクタ
    ## @param lib ライブラリ郡
    ## @return
    #==================================================
    def __init__(
        self,
        lib = {}
    ):
        #==================================================
        # イニシャライズ
        #==================================================
        smach.State.__init__(
            self,
            outcomes = ["next", "loop", "reset", "except"]
        )

        self._lib = lib


        #==================================================
        # ROSインタフェース
        #==================================================


        return




    #==================================================
    ## @fn __del__
    ## @brief デストラクタ
    ## @param
    ## @return
    #==================================================
    def __del__(self):
        #==================================================
        # ファイナライズ
        #==================================================

        return



    #==================================================
    ## @fn execute
    ## @brief 実行関数
    ## @param 
    ## @return
    #==================================================
    def execute(
        self,
        userdata
    ):
        inf_rad_sorted = self._lib["scan"].getLaserInfRad()
        position_meter = self._lib["map"].getRobotPointMeter()

        # もし、進行可能な空間がない場合、かつロボットが動いていない場合、トライアルをリセットする
        if len(inf_rad_sorted) == 0:
            robot_vel = self._lib["nav"].getRobotVel()
            if robot_vel < 0.001:
                rospy.loginfo("escaping now ...(MakeDirCan)")
                self._lib["record"].recordGoal(False)
                self._lib["record"].recordStatus("stack")
                self._lib["record"].recordTime(state="stop")
                self._lib["nav"].resetTrial()

                return "reset"

        # 現在のロボットの後進方向から一番近いinf_radを発見する
        nearest_inf_rad_to_present_rad = inf_rad_sorted[0] - math.pi
        for i in range(len(inf_rad_sorted)):
            if math.cos(inf_rad_sorted[i] - position_meter[2] - math.pi) >= math.cos(nearest_inf_rad_to_present_rad - position_meter[2] - math.pi):
                nearest_inf_rad_to_present_rad = inf_rad_sorted[i]
        # ロボットを回転させる（位置調整のため）
        self._lib["nav"].sendRotationTwist(nearest_inf_rad_to_present_rad - math.pi, position_meter[2])

        rospy.sleep(1.0)

        # 交差点において進行可能な方向をリストアップする
        direction_candidates_inf_rad_sorted_idx = [-1,-1,-1,-1] # [北、南、東、西]
        for i in range(len(inf_rad_sorted)):
            if 0.70 < math.cos(inf_rad_sorted[i]):      # 北 
                direction_candidates_inf_rad_sorted_idx[0] = i
            elif -0.70 > math.cos(inf_rad_sorted[i]):   # 南
                direction_candidates_inf_rad_sorted_idx[1] = i
            elif -0.70 > math.sin(inf_rad_sorted[i]):   # 東
                direction_candidates_inf_rad_sorted_idx[2] = i
            elif 0.70 < math.sin(inf_rad_sorted[i]):    # 西
                direction_candidates_inf_rad_sorted_idx[3] = i

        print("direction_candidates_inf_rad_sorted_idx = {}".format(direction_candidates_inf_rad_sorted_idx))
        
        rospy.set_param(rospy.get_name() + "/inf_rad_sorted", inf_rad_sorted)
        rospy.set_param(rospy.get_name() + "/direction_candidates_inf_rad_sorted_idx", direction_candidates_inf_rad_sorted_idx)

        
        return "next"



#==================================================
## @class UpdateXTable
## @berif 
#==================================================
class UpdateXTable(
    smach.State
):
    #==================================================
    ## @fn __init__
    ## @brief コンストラクタ
    ## @param lib ライブラリ郡
    ## @return
    #==================================================
    def __init__(
        self,
        lib = {}
    ):
        #==================================================
        # イニシャライズ
        #==================================================
        smach.State.__init__(
            self,
            outcomes = ["next", "loop", "except"]
        )

        self._lib = lib

        #==================================================
        # ROSインタフェース
        #==================================================

        return



    #==================================================
    ## @fn __del__
    ## @brief デストラクタ
    ## @param
    ## @return
    #==================================================
    def __del__(self):
        #==================================================
        # ファイナライズ
        #==================================================

        return



    #==================================================
    ## @fn execute
    ## @brief 実行関数
    ## @param robot_decided_direction
    ## @return
    #==================================================
    def execute(
        self,
        userdata
    ):
        q_table = rospy.get_param(rospy.get_name() + "/q_table", [])
        x_table = rospy.get_param(rospy.get_name() + "/x_table", [])

        # 交差点のx_tableを更新
        position_meter = self._lib["map"].getRobotPointMeter()
        nearest_x = [10000, 10000, 10000]   # 現在地点に一番近い交差点の座標x
        nearest_q = [0,0,0,0]               # 現在地点に一番近い交差点のQ
        nearest_x_table_idx = 0             # 現在地点に一番近い交差点の座標xのインデックス
        if len(x_table) == 0:
            x_table.append(position_meter)
            q_table.append([0,0,0,0])
            nearest_x = position_meter
        else:
            # 現在地点とx_table・q_tableの紐付け
            for i in range(len(x_table)):
                tmp1 = math.sqrt((x_table[i][0] - position_meter[0])**2 + (x_table[i][1] - position_meter[1])**2)
                tmp2 = math.sqrt((nearest_x[0] - position_meter[0])**2 + (nearest_x[1] - position_meter[1])**2)
                if tmp1 < tmp2:
                    nearest_x = x_table[i]
                    nearest_q = q_table[i]
                    nearest_x_table_idx = i
            print(math.sqrt((nearest_x[0] - position_meter[0])**2 + (nearest_x[1] - position_meter[1])**2))    
            # 新しい交差点を見つけたら、x_table・q_tableに追加する
            if math.sqrt((nearest_x[0] - position_meter[0])**2 + (nearest_x[1] - position_meter[1])**2) > 2.0:
                x_table.append(position_meter)
                q_table.append([0,0,0,0])
                nearest_x = position_meter
                nearest_q = [0,0,0,0]
                nearest_x_table_idx = -1
            # 発見済みの交差点を再度見つけたら、x_tableを更新する
            else:
                x_table[nearest_x_table_idx][0] = (x_table[nearest_x_table_idx][0] + position_meter[0]) / 2
                x_table[nearest_x_table_idx][1] = (x_table[nearest_x_table_idx][1] + position_meter[1]) / 2

        rospy.set_param(rospy.get_name() + "/q_table", q_table)
        rospy.set_param(rospy.get_name() + "/x_table", x_table)
        rospy.set_param(rospy.get_name() + "/nearest_x_table_idx", nearest_x_table_idx)


        return "next"



#==================================================
## @class MakeRobotDecideDirection
## @brief 
#==================================================
class MakeRobotDecideDirection(
    smach.State
):
    #==================================================
    ## @fn __init__
    ## @brief コンストラクタ
    ## @param lib ライブラリ郡
    ## @return
    #==================================================
    def __init__(
        self,
        lib = {}
    ):
        #==================================================
        # イニシャライズ
        #==================================================
        smach.State.__init__(
            self,
            outcomes = ["next", "loop", "except"]
        )

        self._lib = lib


        #==================================================
        # ROSインタフェース
        #==================================================

        return



    #==================================================
    ## @fn __del__
    ## @brief デストラクタ
    ## @param
    ## @return
    #==================================================
    def __del__(self):
        #==================================================
        # ファイナライズ
        #==================================================

        return



    #==================================================
    ## @fn execute
    ## @brief 実行関数
    ## @param 
    ## @return
    #==================================================
    def execute(
        self,
        userdata
    ):
        direction_candidates_inf_rad_sorted_idx = rospy.get_param(rospy.get_name() + "/direction_candidates_inf_rad_sorted_idx", [-1,-1,-1,-1])
        q_table = rospy.get_param(rospy.get_name() + "/q_table", [])
        x_table = rospy.get_param(rospy.get_name() + "/x_table", [])
        nearest_x_table_idx = rospy.get_param(rospy.get_name() + "/nearest_x_table_idx", -1)

        # GUIの変更
        self._lib["if"].changeGUI("wait")

        decided_direction = []
        # random時であれば、進行可能な方向から、ランダムな方向を選択する
        if rospy.get_param("/random", "") == True:
            direction_candidates_inf_rad_sorted_idx_trim = [direction_candidates_inf_rad_sorted_idx[i] for i in range(len(direction_candidates_inf_rad_sorted_idx)) if direction_candidates_inf_rad_sorted_idx[i]!=-1]
            rand_direction = random.choice(direction_candidates_inf_rad_sorted_idx_trim)
            decided_direction = [1 if direction_candidates_inf_rad_sorted_idx[i]==rand_direction else 0 for i in range(len(direction_candidates_inf_rad_sorted_idx))]
        # not random時であれば、進行可能な方向から、q_tableが最大の進行方向を選択する
        elif rospy.get_param("/random", "") == False:
            direction_candidates_inf_rad_sorted_idx_trim = [direction_candidates_inf_rad_sorted_idx[i] for i in range(len(direction_candidates_inf_rad_sorted_idx)) if direction_candidates_inf_rad_sorted_idx[i]!=-1]
            q_trim = [q_table[nearest_x_table_idx][i] for i in range(len(q_table[nearest_x_table_idx])) if direction_candidates_inf_rad_sorted_idx[i]!=-1]

            max_q_direction = self._lib["nav"].randomChoices(direction_candidates_inf_rad_sorted_idx_trim, q_trim)
            decided_direction = [1 if direction_candidates_inf_rad_sorted_idx[i]==max_q_direction else 0 for i in range(len(direction_candidates_inf_rad_sorted_idx))]

            print("nearest_x_table_idx = {}".format(nearest_x_table_idx))
            print("q_table = {}".format(q_table))
            print("decided_direction = {}".format(decided_direction))

        else:
            print("/random param error!")
            print(rospy.get_param("/random", ""))

        rospy.set_param(rospy.get_name() + "/robot_decided_direction", decided_direction) # [北、南、東、西]

        # 地図作成を待つ
        rospy.sleep(1)

        return "next"


#==================================================
## @class MakeHumanDecideDirection
## @brief 
#==================================================
class MakeHumanDecideDirection(
    smach.State
):
    #==================================================
    ## @fn __init__
    ## @brief コンストラクタ
    ## @param lib ライブラリ群
    ## @return
    #==================================================
    def __init__(
        self,
        lib = {}
    ):
        #==================================================
        # イニシャライズ
        #==================================================
        smach.State.__init__(
            self,
            outcomes = ["next", "loop", "except"]
        )

        self._lib = lib

        #==================================================
        # ROSインタフェース
        #==================================================

        return



    #==================================================
    ## @fn __del__
    ## @brief デストラクタ
    ## @param
    ## @return
    #==================================================
    def __del__(self):
        #==================================================
        # ファイナライズ
        #==================================================

        return



    #==================================================
    ## @fn execute
    ## @brief 実行関数
    ## @param 
    ## @return
    #==================================================
    def execute(
        self,
        userdata
    ):

        direction_candidates_inf_rad_sorted_idx = rospy.get_param(rospy.get_name() + "/direction_candidates_inf_rad_sorted_idx", [-1,-1,-1,-1])

        position_meter = self._lib["map"].getRobotPointMeter()

        # GUIの変更
        self._lib["if"].changeGUI("judge")

        # 進行可能な方向から、ランダムに進行方向を選択する
        #direction_candidates_inf_rad_sorted_idx_trim = [direction_candidates_inf_rad_sorted_idx[i] for i in range(len(direction_candidates_inf_rad_sorted_idx)) if direction_candidates_inf_rad_sorted_idx[i]!=-1]
        #rand_direction = random.choice(direction_candidates_inf_rad_sorted_idx_trim)
        #decided_direction = [1 if direction_candidates_inf_rad_sorted_idx[i]==rand_direction else 0 for i in range(len(direction_candidates_inf_rad_sorted_idx))]
        #rospy.sleep(5)

        # ゲームパッドで被験者が選択した方向を出力する
        decided_direction = []
        while True:
            human_direction = self._lib["if"].waitGamepad()                                                     # [上、下、右、左]

            if human_direction == None:
                print("input timeout ...")

                continue

            human_direction = self._lib["if"].changeGamepadInputUDRLtoNSEW(human_direction, position_meter[2])  # [北、南、東、西]

            if direction_candidates_inf_rad_sorted_idx[[i for i in range(len(human_direction)) if human_direction[i]==1][0]] == -1:
                print("plz select correct direction !!!")
            else:
                decided_direction = human_direction

                break

        rospy.set_param(rospy.get_name() + "/human_decided_direction", decided_direction) # [北、南、東、西]


        return "next"


#==================================================
## @class DecideDirection
## @berif 
#==================================================
class DecideDirection(
    smach.State
):
    #==================================================
    ## @fn __init__
    ## @brief コンストラクタ
    ## @param lib ライブラリ群
    ## @return
    #==================================================
    def __init__(
        self,
        lib = {}
    ):
        #==================================================
        # イニシャライズ
        #==================================================
        smach.State.__init__(
            self,
            outcomes = ["next", "loop", "except"]
        )

        self._lib = lib

        #==================================================
        # ROSインタフェース
        #==================================================

        return




    #==================================================
    ## @fn __del__
    ## @brief デストラクタ
    ## @param
    ## @return
    #==================================================
    def __del__(self):
        #==================================================
        # ファイナライズ
        #==================================================

        return



    #==================================================
    ## @fn execute
    ## @brief 実行関数
    ## @param 
    ## @return
    #==================================================
    def execute(
        self,
        userdata
    ):
        inf_rad_sorted = rospy.get_param(rospy.get_name() + "/inf_rad_sorted", [])
        direction_candidates_inf_rad_sorted_idx = rospy.get_param(rospy.get_name() + "/direction_candidates_inf_rad_sorted_idx", [-1,-1,-1,-1])  # [北、南、東、西]
        robot_decided_direction = rospy.get_param(rospy.get_name() + "/robot_decided_direction", [0,0,0,0])  # [北、南、東、西]
        human_decided_direction = rospy.get_param(rospy.get_name() + "/human_decided_direction", [0,0,0,0])  # [北、南、東、西]

        print("inf_rad_sorted = {}".format(inf_rad_sorted))
        print("direction_candidates_inf_rad_sorted_idx = {}".format(direction_candidates_inf_rad_sorted_idx))
        print("robot_decided_direction = {}".format(robot_decided_direction))
        print("human_decided_direction = {}".format(human_decided_direction))

        position_meter = self._lib["map"].getRobotPointMeter()

        # GUIの変更
        self._lib["if"].changeGUI("move")

        decided_direction = []

        pilot = random.choice(("robot", "human", "human", "human"))
        if pilot == "robot":
            print("chose robot's decided direction !")
            decided_direction = robot_decided_direction
        else:
            print("chose human's decided direction !")
            decided_direction = human_decided_direction

        idx = [direction_candidates_inf_rad_sorted_idx[i] for i,ele in enumerate(decided_direction) if decided_direction[i]==1][0]
        decided_direction_inf_rad_sorted = inf_rad_sorted[idx]

        rospy.set_param(rospy.get_name() + "/pilot", pilot)
        rospy.set_param(rospy.get_name() + "/decided_direction", decided_direction)
        rospy.set_param(rospy.get_name() + "/decided_direction_inf_rad_sorted", decided_direction_inf_rad_sorted)

        self._lib["record"].saveRecordPilot()
        self._lib["record"].saveRecordDirection()


        return "next"


#==================================================
## @class CheckErrP
## @berif 
#==================================================
class CheckErrP(
    smach.State
):
    #==================================================
    ## @fn __init__
    ## @brief コンストラクタ
    ## @param lib ライブラリ郡
    ## @return
    #==================================================
    def __init__(
        self,
        lib = {}
    ):
        #==================================================
        # イニシャライズ
        #==================================================
        smach.State.__init__(
            self,
            outcomes = ["next", "loop", "except"]
        )

        self._lib = lib

        #==================================================
        # ROSインタフェース
        #==================================================

        return



    #==================================================
    ## @fn __del__
    ## @brief デストラクタ
    ## @param
    ## @return
    #==================================================
    def __del__(self):
        #==================================================
        # ファイナライズ
        #==================================================

        return



    #==================================================
    ## @fn execute
    ## @brief 実行関数
    ## @param 
    ## @return
    #==================================================
    def execute(
        self,
        userdata
    ):
        # be時であれば、被験者のコマンド入力をスキップする
        '''if rospy.get_param("/exp_type", "") == "be":

            return "next"
        '''
        pilot = rospy.get_param(rospy.get_name() + "/pilot", "None")
        robot_decided_direction = rospy.get_param(rospy.get_name() + "/robot_decided_direction", [])  # [北、南、東、西]
        human_decided_direction = rospy.get_param(rospy.get_name() + "/human_decided_direction", [])  # [北、南、東、西]
        decided_direction_inf_rad_sorted = rospy.get_param(rospy.get_name() + "/decided_direction_inf_rad_sorted", 0)

        position_meter = self._lib["map"].getRobotPointMeter()

        # 前進方向が選択された場合、ロボットが少し前進する(ErrP誘発のため)
        if 0.70 < math.cos(decided_direction_inf_rad_sorted - position_meter[2]):
            # decided_direction_inf_rad_sorted方向に前進する
            self._lib["nav"].sendRunTwist(
                decided_direction_inf_rad_sorted,
                position_meter[2],
                target_time = 1.0
            )
        # 後退方向が選択された場合、回れ右をする#ロボットが少し後退する(ErrP誘発のため)
            """elif -0.70 > math.cos(decided_direction_inf_rad_sorted - position_meter[2]):
            # decided_direction_inf_rad_sorted方向に後進する
            self._lib["nav"].sendRunTwist(
                decided_direction_inf_rad_sorted,
                position_meter[2],
                lin_speed = -0.3,
                target_time = 1.0
            )"""
        elif -0.70 > math.cos(decided_direction_inf_rad_sorted - position_meter[2]):
            # decided_direction_inf_rad_sorted方向に回転する
            self._lib["nav"].sendRotationTwist(decided_direction_inf_rad_sorted,position_meter[2],)
        # それ以外の方向が選択された場合、ロボットが回転する(ErrP誘発のため)
        else:
            self._lib["nav"].sendRotationTwist(decided_direction_inf_rad_sorted, position_meter[2])

        rospy.sleep(1.0)

        # ErrPが発生した場合、移動前の位置に戻って再度進行方向の選択を行う
        # TODO ErrPの認識結果をreward則に反映する
        errp = 0
        if pilot == "robot": # ロボットの決定した進行方向が選択され、
            if robot_decided_direction != human_decided_direction: # 人間とロボットの選択した進行方向が異なる場合
                print("ErrP evoked !!!")
                errp = 1    # ErrP発生

        rospy.set_param(rospy.get_name() + "/errp", errp)
        rospy.set_param(rospy.get_name() + "/position_meter", position_meter)

        self._lib["record"].saveRecordErrP()


        return "next"


#==================================================
## @class UpdateQTable
## @berif 
#==================================================
class UpdateQTable(
    smach.State
):
    #==================================================
    ## @fn __init__
    ## @brief コンストラクタ
    ## @param lib ライブラリ群
    ## @return
    #==================================================
    def __init__(
        self,
        lib = {}
    ):
        #==================================================
        # イニシャライズ
        #==================================================
        smach.State.__init__(
            self,
            outcomes = ["next", "loop", "except"]
        )

        self._lib = lib

        #==================================================
        # ROSインタフェース
        #==================================================

        return



    #==================================================
    ## @fn __del__
    ## @brief デストラクタ
    ## @param
    ## @return
    #==================================================
    def __del__(self):
        #==================================================
        # ファイナライズ
        #==================================================

        return



    #==================================================
    ## @fn execute
    ## @brief 実行関数
    ## @param robot_decided_direction
    def execute(
        self,
        userdata
    ):

        decided_direction   = rospy.get_param(rospy.get_name() + "/decided_direction", [])              # [北、南、東、西]
        q_table             = rospy.get_param(rospy.get_name() + "/q_table", [])
        x_table             = rospy.get_param(rospy.get_name() + "/x_table", [])
        nearest_x_table_idx = rospy.get_param(rospy.get_name() + "/nearest_x_table_idx", -1)
        errp                = rospy.get_param(rospy.get_name() + "/errp", 0)

        # 交差点のq_tableを更新
        # TODO ErrPの認識結果をreward則に反映する
        reward = 1
        if errp == 1: # ErrPが発生した場合、
            reward = -3 # 罰則を与える
        decided_direction_idx = [i for i in range(len(decided_direction)) if decided_direction[i]==1][0]
        q_table[nearest_x_table_idx][decided_direction_idx] += reward

        print("q_table = {}".format(q_table))
        print("x_table = {}".format(x_table))
        print("errp = {}".format(errp))

        rospy.set_param(rospy.get_name() + "/q_table", q_table)

        self._lib["record"].saveRecordQTable()
        self._lib["record"].saveRecordXTable()

        #if errp == 1:

            #return "err"
        
        #else:
        
        return "next"


#==================================================
## @class GoToCorrectDirection
## @berif 
#==================================================
class GoToCorrectDirection(
    smach.State
):
    #==================================================
    ## @fn __init__
    ## @brief コンストラクタ
    ## @param lib ライブラリ郡
    ## @return
    #==================================================
    def __init__(
        self,
        lib = {}
    ):
        #==================================================
        # イニシャライズ
        #==================================================
        smach.State.__init__(
            self,
            outcomes = ["next", "loop", "reset", "restart", "except"]
        )

        self._lib = lib

        #==================================================
        # ROSインタフェース
        #==================================================

        return



    #==================================================
    ## @fn __del__
    ## @brief デストラクタ
    ## @param
    ## @return
    #==================================================
    def __del__(self):
        #==================================================
        # ファイナライズ
        #==================================================

        return



    #==================================================
    ## @fn execute
    ## @brief 実行関数
    ## @param 
    ## @return
    #==================================================
    def execute(
        self,
        userdata
    ):
        decided_direction_inf_rad_sorted = rospy.get_param(rospy.get_name() + "/decided_direction_inf_rad_sorted", 0)

        # decided_direction_inf_rad_sorted方向に2.0m進行する
        position_meter = self._lib["map"].getRobotPointMeter()
        inf_points_meter = self._lib["scan"].getLaserInfPointMeter(
            [decided_direction_inf_rad_sorted],
            position_meter,
            distance = 1.7
        )
        self._lib["nav"].sendMeterGoal(
            inf_points_meter[0],
            decided_direction_inf_rad_sorted
        )

        # ナビゲーションがスタックした場合、トライアルをリセットする
        for s in self._lib["nav"].subNaviStatus():
            if s == 4: 
                print("Navi stack ...(GoToCorre)")
                self._lib["record"].recordGoal(False)
                self._lib["record"].recordStatus("stack")
                self._lib["record"].recordTime(state="stop")
                self._lib["nav"].resetTrial()

                return "reset"

        rospy.sleep(1.0)

        self._lib["record"].saveMap()

        position_meter = self._lib["map"].getRobotPointMeter()

        inf_rad_sorted = self._lib["scan"].getLaserInfRad()

        # もし、進行可能な空間がない場合、かつロボットが動いていない場合、トライアルをリセットする
        if len(inf_rad_sorted) == 0:
            #robot_vel = self._lib["nav"].getRobotVel()
            #if robot_vel < 0.001:
            '''rospy.loginfo("escaping now ...(GoToCorre)")
                self._lib["record"].recordGoal(False)
                self._lib["record"].recordStatus("stack")
                self._lib["record"].recordTime(state="stop")
                self._lib["nav"].resetTrial()'''

            return "next"                      


        # 現在のロボットの後進方向から一番近いinf_radを発見する
        nearest_inf_rad_to_present_rad = inf_rad_sorted[0] - math.pi
        for i in range(len(inf_rad_sorted)):
            if math.cos(inf_rad_sorted[i] - position_meter[2] - math.pi) >= math.cos(nearest_inf_rad_to_present_rad - position_meter[2] - math.pi):
                nearest_inf_rad_to_present_rad = inf_rad_sorted[i]
        if 0.0 < math.cos(nearest_inf_rad_to_present_rad - math.pi - position_meter[2]):
            # ロボットを回転させる（位置調整のため）
            self._lib["nav"].sendRotationTwist(nearest_inf_rad_to_present_rad - math.pi, position_meter[2])


        rospy.sleep(1.0)


        return "next"



#==================================================
## @class CorrectErrDirection
## @berif 
#==================================================
class CorrectErrDirection(
    smach.State
):
    #==================================================
    ## @fn __init__
    ## @brief コンストラクタ
    ## @param lib ライブラリ郡
    ## @return
    #==================================================
    def __init__(
        self,
        lib = {}
    ):
        #==================================================
        # イニシャライズ
        #==================================================
        smach.State.__init__(
            self,
            outcomes = ["next", "loop", "except"]
        )

        self._lib = lib

        #==================================================
        # ROSインタフェース
        #==================================================

        return



    #==================================================
    ## @fn __del__
    ## @brief デストラクタ
    ## @param
    ## @return
    #==================================================
    def __del__(self):
        #==================================================
        # ファイナライズ
        #==================================================

        return



    #==================================================
    ## @fn execute
    ## @brief 実行関数
    ## @param 
    ## @return
    #==================================================
    def execute(
        self,
        userdata
    ):
        position_meter = rospy.get_param(rospy.get_name() + "/position_meter", [])

        # ロボットを元の位置に戻す
        self._lib["nav"].sendMeterGoal(
            position_meter,
            position_meter[2]
        )

        # ナビゲーションがスタックした場合、トライアルをリセットする
        for s in self._lib["nav"].subNaviStatus():
            if s == 4:
                print("Navi stack ...(CorrectErr")
                self._lib["record"].recordGoal(False)
                self._lib["record"].recordStatus("stack")
                self._lib["record"].recordTime(state="stop")
                self._lib["nav"].resetTrial()

                return "reset"

        #rad_now = self._lib["map"].getRobotPointMeter()[2]

        # ロボットを回転させる（位置調整のため）
        #self._lib["nav"].sendRotationTwist(position_meter[2], rad_now)

        rospy.sleep(1.0)

        self._lib["record"].saveMap()

        return "next"



#==================================================
## @class End
## @berif 終了ステート
#==================================================
class End(
    smach.State
):
    #==================================================
    ## @fn __init__
    ## @brief コンストラクタ
    ## @param lib ライブラリ郡
    ## @return
    #==================================================
    def __init__(
        self,
        lib = {}
    ):
        #==================================================
        # イニシャライズ
        #==================================================
        smach.State.__init__(
            self,
            outcomes = ["end"]
        )

        self._lib = lib
        return




    #==================================================
    ## @fn __del__
    ## @brief デストラクタ
    ## @param
    ## @return
    #==================================================
    def __del__(self):
        #==================================================
        # ファイナライズ
        #==================================================

        return




    #==================================================
    ## @fn execute
    ## @brief 実行関数
    ## @param userdata
    ## @return
    #==================================================
    def execute(
        self,
        userdata
    ):

        return "end"




#==================================================
## @class Except
## @brief 例外ステート
#==================================================
class Except(
    smach.State
):
    #==================================================
    ## @fn __init__
    ## @brief コンストラクタ
    ## @param lib ライブラリ群
    ## @return
    #==================================================
    def __init__(
        self,
        lib = {}
    ):
        #==================================================
        # イニシャライズ
        #==================================================
        smach.State.__init__(
            self,
            outcomes = ["except"]
        )

        self._lib = lib

        return




    #==================================================
    ## @fn __del__
    ## @brief デストラクタ
    ## @param
    ## @return
    #==================================================
    def __del__(self):
        #==================================================
        # ファイナライズ
        #==================================================

        return




    #==================================================
    ## @fn execute
    ## @brief 実行関数
    ## @param userdata
    ## @return
    #==================================================
    def execute(
        self,
        userdata
    ):

        return "except"
