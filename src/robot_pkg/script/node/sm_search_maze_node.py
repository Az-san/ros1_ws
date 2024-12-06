#!/usr/bin/env python3
# -*- coding: utf-8 -*-




#==================================================

## @file sm_search_maze_node.py
## @author Kentaro NAKAMURA
## @brief 迷路を探索するROSノード

#==================================================




#==================================================

# import

#==================================================
import sys
import roslib
import rospy
import os

import smach
import smach_ros

import sm_main
from sm_main import *

sys.path.append(roslib.packages.get_pkg_dir("robot_pkg") + "/script/import")
from common_import import *

sys.path.append(roslib.packages.get_pkg_dir("robot_pkg") + "/script/lib")
from lib_map import *
from lib_nav import *
from lib_raspi import *
from lib_scan import *
from lib_record import *
from lib_if import *



#==================================================

# グローバル

#==================================================
GP_DEFAULT_START_STATE = "Start"




#==================================================

## @class StateMachine
## @brief ステートマシンクラス

#==================================================
class StateMachine:
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
        self._libmap = LibMap()
        self._libnav = LibNav()
        self._libraspi = LibRaspi()
        self._libscan = LibScan()
        self._librecord = LibRecord()
        self._libif = LibIF()

        self._lib = {
            "map": self._libmap,
            "nav": self._libnav,
            "raspi": self._libraspi,
            "scan": self._libscan,
            "record": self._librecord,
            "if": self._libif,
        }


        #==================================================

        # イニシャライズ

        #==================================================
        #スタートステートの選択
        start_state = GP_DEFAULT_START_STATE

        #ステートマシンの宣言
        self._ssm = smach.StateMachine(outcomes = ["exit"])

        with self._ssm:
            smach.StateMachine.add(
                "Init",
                Init(self._lib), 
                transitions = {
                    "next":"Wait4Start",
                    "except":"Except"
                }
            )
            smach.StateMachine.add(
                "Wait4Start",
                Wait4Start(self._lib),
                transitions = {
                    "next":start_state,
                    "except":"Except"
                }
            )
            smach.StateMachine.add(
                "Start",
                Start(self._lib),
                transitions = {
                    "next":"StartTrial",
                    "except":"Except"
                }
            )
            smach.StateMachine.add(
                "StartTrial",
                StartTrial(self._lib),
                transitions = {
                    "next":"CheckIntersection",
                    "restart":"Start",
                    "loop":"StartTrial",
                    "except":"Except"
                }
            )
            smach.StateMachine.add(
                "CheckIntersection",
                CheckIntersection(self._lib),
                transitions = {
                    "true":"MakeDirectionCandidates",
                    "false":"GoAhead",
                    "loop":"CheckIntersection",
                    "except":"Except"
                }
            )
            smach.StateMachine.add(
                "GoAhead",
                GoAhead(self._lib),
                transitions = {
                    "next":"CheckIntersection",
                    "loop":"GoAhead",
                    "reset":"Start",
                    "except":"Except"
                }
            )
            smach.StateMachine.add(
                "MakeDirectionCandidates",
                MakeDirectionCandidates(self._lib),
                transitions = {
                    "next":"UpdateXTable",
                    "loop":"MakeDirectionCandidates",
                    "reset":"Start",
                    "except":"Except"
                }
            )
            smach.StateMachine.add(
                "UpdateXTable",
                UpdateXTable(self._lib),
                transitions = {
                    "next":"MakeRobotDecideDirection",
                    "loop":"UpdateXTable",
                    "except":"Except"
                }
            )
            smach.StateMachine.add(
                "MakeRobotDecideDirection",
                MakeRobotDecideDirection(self._lib),
                transitions = {
                    "next":"MakeHumanDecideDirection",
                    "loop":"MakeRobotDecideDirection",
                    "except":"Except"
                }
            )
            smach.StateMachine.add(
                "MakeHumanDecideDirection",
                MakeHumanDecideDirection(self._lib),
                transitions = {
                    "next":"DecideDirection",
                    "loop":"MakeHumanDecideDirection",
                    "except":"Except"
                }
            )
            smach.StateMachine.add(
                "DecideDirection",
                DecideDirection(self._lib),
                transitions = {
                    "next":"CheckErrP",
                    "loop":"DecideDirection",
                    "except":"Except"
                }
            )
            smach.StateMachine.add(
                "CheckErrP",
                CheckErrP(self._lib),
                transitions = {
                    "next":"UpdateQTable",
                    "loop":"CheckErrP",
                    "except":"Except"
                }
            )
            smach.StateMachine.add(
                "UpdateQTable",
                UpdateQTable(self._lib),
                transitions = {
                    "corr":"GoToCorrectDirection",
                    "err":"CorrectErrDirection",
                    "loop":"UpdateQTable",
                    "except":"Except"
                }
            )
            smach.StateMachine.add(
                "GoToCorrectDirection",
                GoToCorrectDirection(self._lib),
                transitions = {
                    "next":"CheckIntersection",
                    "loop":"GoToCorrectDirection",
                    "reset":"StartTrial",
                    "restart":"Start",
                    "except":"Except"
                }
            )
            smach.StateMachine.add(
                "CorrectErrDirection",
                CorrectErrDirection(self._lib),
                transitions = {
                    "next":"MakeDirectionCandidates",
                    "loop":"CorrectErrDirection",
                    "except":"Except"
                }
            )
            smach.StateMachine.add(
                "End",
                End(self._lib),
                transitions = {
                    "end":"exit",
                }
            )
            smach.StateMachine.add(
                "Except",
                Except(self._lib),
                transitions = {
                    "except":"exit"
                }
            )

        sris = smach_ros.IntrospectionServer("ssm", self._ssm, "/SM_ROOT")
        sris.start()


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
        for key in self._lib.keys():
            self._lib[key].delete()

        del self._ssm


        return




    #==================================================
    
    ## @fn proc
    ## @berif 処理関数
    ## @param
    ## @return

    #==================================================
    def proc(
        self
    ):
        self._ssm.execute()


        return




#==================================================

# メイン

#==================================================
if __name__ == "__main__":
    rospy.init_node(os.path.basename(__file__).split(".")[0])

    state_machine = StateMachine()

    rospy.on_shutdown(state_machine.delete)

    state_machine.proc()

    rospy.signal_shutdown("")
