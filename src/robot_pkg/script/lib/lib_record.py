#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#==================================================
## @file librecord
## @original_author Kentaro NAKAMURA
## @author Takumi FUJI
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
## @class LibRecord
## @brief 自作ライブラリクラス
#==================================================
class LibRecord:
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
        dt = datetime.today() # 時間まで
        self.date = "{}_{}_{}_{}_{}_{}".format(dt.year,dt.month,dt.day,dt.hour,dt.minute,dt.second)
        self.sub = 0
        self.exp_cnt = 0
        self.maze = rospy.get_param("/maze", "")
        self.data_name = "{}_{}_{}_{}".format(self.date,self.sub,self.exp_cnt,self.maze)
        self.data_path = roslib.packages.get_pkg_dir("robot_pkg") + "/data" + "/" + self.data_name
        self.robot_decided_direction_list = []
        self.human_decided_direction_list = []
        self.decided_direction_list = []
        self.errp_list = []
        self.pilot_list = []
        self.x_id_list = []
        self.fork_num_list = []
        self.time_list = []
        self.record_start_time = -1.0
        self.reset_cnt = 0
        self.goal_cnt = 0
        self.trial_cnt = 0
        self.x_len = 0

        #==================================================
        # イニシャライズ
        #==================================================


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
    ## @fn initPath
    ## @brief データ保存先の初期化
    ## @param
    ## @return
    #==================================================
    def initSaveDataPath(
        self,
    ):
        print(self.sub)
        self.data_name = "{}_{}_{}_{}".format(self.date,self.sub,self.exp_cnt,self.maze)
        self.data_path = roslib.packages.get_pkg_dir("robot_pkg") + "/data" + "/" + self.data_name
        print(self.data_path)
        return

    #==================================================
    ## @fn updateInfo
    ## @brief 
    ## @param
    ## @return
    #==================================================
    def updateInfo(
        self, sub, exp_cnt, info, MiniMap
    ):
        self.sub = sub
        self.exp_cnt = exp_cnt
        self.info = info
        self.MiniMap = MiniMap

        return 

    #==================================================
    ## @fn saveInfo
    ## @brief 
    ## @param
    ## @return
    #==================================================
    def saveInfo(
        self,
        ErrRate,SocketActive,TTLActive
    ):
        f = open(self.data_path + '/info.txt', 'a')
        f.write('Date: '+ self.date + '\n')
        f.write('被験者番号: '+ self.sub + '\n')
        f.write('実験番号: '+ self.exp_cnt + '\n')
        f.write('エラー率[%]: ' + str(ErrRate*10) + '\n')
        f.write('SocketActive: '+str(SocketActive) + '\n')
        f.write('TTLActive: '+str(TTLActive) + '\n')
        f.write('MiniMap Visible: '+str(self.MiniMap) + '\n')
        f.write('備考: '+ self.info + '\n')

        return

    #==================================================
    ## @fn incExpCnt
    ## @brief 
    ## @param
    ## @return
    #==================================================
    def incExpCnt(
        self
    ):
        self.exp_cnt += 1

        dt = datetime.today() # 時間まで
        self.date = "{}_{}_{}_{}_{}_{}".format(dt.year,dt.month,dt.day,dt.hour,dt.minute,dt.second)
        self.record_start_time = -1.0
        self.reset_cnt = 0
        self.goal_cnt = 0
        self.trial_cnt = 0

        return 



    #==================================================
    ## @fn getExpCnt
    ## @brief 
    ## @param
    ## @return
    #==================================================
    def getExpCnt(
        self
    ):
    
        return self.exp_cnt




    #==================================================
    ## @fn incTrialCnt
    ## @brief 
    ## @param
    ## @return
    #==================================================
    def incTrialCnt(
        self
    ):
        self.trial_cnt += 1
        print("self.trial_cnt = {}".format(self.trial_cnt))

        return 



    #==================================================
    ## @fn getTrialCnt
    ## @brief 
    ## @param
    ## @return
    #==================================================
    def getTrialCnt(
        self
    ):
    
        return self.trial_cnt




    #==================================================
    ## @fn getResetCnt
    ## @brief 
    ## @param
    ## @return
    #==================================================
    def getResetCnt(
        self
    ):
    
        return self.reset_cnt



    #==================================================
    ## @fn initPath
    ## @brief データ保存先の初期化
    ## @param
    ## @return
    #==================================================
    def initPath(
        self,
        exp_type
    ):
        self.robot_decided_direction_list = []
        self.human_decided_direction_list = []
        self.decided_direction_list = []
        self.errp_list = []
        self.pilot_list = []

        self.initSaveDataPath()
        cd = roslib.packages.get_pkg_dir("robot_pkg") + "/data"
        if not self.data_name in os.listdir(cd):
            os.mkdir(cd + "/" + self.data_name)

        return


    #==================================================
    ## @fn incGoalCnt
    ## @brief 
    ## @param
    ## @return
    #==================================================
    def incGoalCnt(
        self
    ):
        self.goal_cnt += 1

        return 


    #==================================================
    ## @fn getGoalCnt
    ## @brief 
    ## @param
    ## @return
    #==================================================
    def getGoalCnt(
        self
    ):
    
        return self.goal_cnt


    #==================================================
    ## @fn saveRecordQTable
    ## @brief 
    ## @param
    ## @return
    #==================================================
    def saveRecordQTable(
        self
    ):
        path = self.data_path + "/QTable.pkl"
        q_table = rospy.get_param(rospy.get_name() + "/q_table", [])
        with open(path, 'wb') as web:
            pickle.dump(q_table , web)

        print("QTable saved !!!")

        return


    #==================================================
    ## @fn saveRecordXTable
    ## @brief 
    ## @param
    ## @return
    #==================================================
    def saveRecordXTable(
        self
    ):
        path = self.data_path + "/XTable.pkl"
        x_table = rospy.get_param(rospy.get_name() + "/x_table", [])
        with open(path, 'wb') as web:
            pickle.dump(x_table , web)

        print("XTable saved !!!")

        return

    #==================================================
    ## @fn saveRecordDirection
    ## @brief 
    ## @param
    ## @return
    #==================================================
    def saveRecordDirection(
        self
    ):
        path = self.data_path + "/RobotDecidedDirection.pkl"
        robot_decided_direction = rospy.get_param(rospy.get_name() + "/robot_decided_direction", [])  # [北、南、東、西]
        self.robot_decided_direction_list.append(robot_decided_direction)
        with open(path, 'wb') as web:
            pickle.dump(self.robot_decided_direction_list , web)

        print("robot decided direction saved !!!")

        path = self.data_path + "/HumanDecidedDirection.pkl"
        human_decided_direction = rospy.get_param(rospy.get_name() + "/human_decided_direction", [])  # [北、南、東、西]
        self.human_decided_direction_list.append(human_decided_direction)
        with open(path, 'wb') as web:
            pickle.dump(self.human_decided_direction_list , web)

        print("human decided direction saved !!!")

        path = self.data_path + "/DecidedDirection.pkl"
        decided_direction = rospy.get_param(rospy.get_name() + "/decided_direction", []) # [北、南、東、西]
        self.decided_direction_list.append(decided_direction)
        with open(path, 'wb') as web:
            pickle.dump(self.decided_direction_list , web)

        print("decided direction saved !!!")

        return


    #==================================================
    ## @fn saveRecordErrP
    ## @brief 
    ## @param
    ## @return
    #==================================================
    def saveRecordErrP(
        self
    ):
        path = self.data_path + "/ErrP.pkl"
        errp = rospy.get_param(rospy.get_name() + "/errp", 0)
        self.errp_list.append(errp)
        with open(path, 'wb') as web:
            pickle.dump(self.errp_list , web)

        print("ErrP saved !!!")

        return


    #==================================================
    ## @fn saveRecordPilot
    ## @brief 
    ## @param
    ## @return
    #==================================================
    def saveRecordPilot(
        self
    ):
        path = self.data_path + "/Pilot.pkl"
        pilot = rospy.get_param(rospy.get_name() + "/pilot", "None")
        self.pilot_list.append(pilot)
        with open(path, 'wb') as web:
            pickle.dump(self.pilot_list , web)

        print("Pilot saved !!!")

        return
        
        
    #==================================================
    ## @fn saveRecordXid
    ## @brief 
    ## @param
    ## @return
    #==================================================
    def saveRecordXid(
        self
    ):
        path = self.data_path + "/x_id.pkl"
        xid = rospy.get_param(rospy.get_name() + "/nearest_x_table_idx", "None")
        self.x_id_list.append(xid)
        with open(path, 'wb') as web:
            pickle.dump(self.x_id_list , web)

        print("X_id saved !!!")

        return


    #==================================================
    ## @fn saveRecordFork
    ## @brief 
    ## @param
    ## @return
    #==================================================
    def saveRecordFork(
        self, inf_rad_sorted
    ):
        path = self.data_path + "/fork_num.pkl"
        self.fork_num_list.append(len(inf_rad_sorted))
        with open(path, 'wb') as web:
            pickle.dump(self.fork_num_list , web)

        print("Fork_num saved !!!")

        return

    #==================================================
    ## @fn saveMap
    ## @brief 
    ## @param
    ## @return
    #==================================================
    def saveMap(
        self
    ):
        path = self.data_path + "/map"
        cmd = "rosrun map_server map_saver -f {}".format(path)
        Popen(cmd.split(" "))
        # 地図保存を待つ 保存中にnavするとnavが停止する？ 20201214
        rospy.sleep(0.5)
        path = roslib.packages.get_pkg_dir("robot_pkg") + "/io/map"
        cmd = "rosrun map_server map_saver -f {}".format(path)
        Popen(cmd.split(" "))
        rospy.sleep(0.5)

        print("map saved !!!")

        return


    #==================================================
    ## @fn recordTime
    ## @brief 
    ## @param
    ## @return
    #==================================================
    def recordTime(
        self,
        state = "start"
    ):
        # 開始の時刻を保存
        if state == "start":
            self.record_start_time = rospy.Time.now().to_sec()
        # 経過した時刻を取得
        elif state == "lap":
            record_time = rospy.Time.now().to_sec() - self.record_start_time
            self.time_list.append(record_time)
            path = self.data_path + "/Time.pkl"
            with open(path, 'wb') as web:
                pickle.dump(self.time_list , web)

            print("record time = {}".format(record_time))

        return



    #==================================================
    ## @fn recordGoal
    ## @brief 
    ## @param
    ## @return
    #==================================================
    def recordGoal(
        self,
        status
    ):
        path = self.data_path + "/Goal.pkl"
        with open(path, 'wb') as web:
            pickle.dump(status , web)

        print("Goal = {}".format(status))

        return


    #==================================================
    ## @fn recordStatus
    ## @brief 
    ## @param
    ## @return
    #==================================================
    def recordStatus(
        self,
        status
    ):
        path = self.data_path + "/Status.pkl"
        with open(path, 'wb') as web:
            pickle.dump(status , web)

        print("Status = {}".format(status))

        return



    #==================================================
    ## @fn loadRecordQTable
    ## @brief 
    ## @param
    ## @return
    #==================================================
    def loadRecordQTable(
        self,
        save_date_path
    ):
        path = save_date_path + "/QTable.pkl"
        with open(path, 'rb') as web:
            data = pickle.load(web)

        return data


    #==================================================
    ## @fn loadRecordXTable
    ## @brief 
    ## @param
    ## @return
    #==================================================
    def loadRecordXTable(
        self,
        save_date_path
    ):
        path = save_date_path + "/XTable.pkl"
        with open(path, 'rb') as web:
            data = pickle.load(web)

        return data


