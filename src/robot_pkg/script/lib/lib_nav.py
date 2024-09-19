#!/usr/bin/env python3
# -*- coding: utf-8 -*-




#==================================================

## @file libnav
## @author Kentaro NAKAMURA
## @modified for Noetic by Takumi FUJI
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

## @class LibNav
## @brief ナビゲーションを行うライブラリ

#==================================================
class LibNav:
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
        self.sub_val_data = Twist()
        self.sub_status_data = -1
        self.goal_point_meter = [0.0, 0.0, 0.0]

        #==================================================

        # ROSインタフェース

        #==================================================
        self.client = actionlib.SimpleActionClient(
            "/move_base",
            MoveBaseAction,
        )

        self.pub_vel = rospy.Publisher(
            'cmd_vel', 
            Twist, 
            queue_size=1
        )

        self._sub_vel = rospy.Subscriber(
            "/gazebo/model_states",
            ModelStates,
            self.velCallback,
            queue_size = 1
        )

        self._sub_status = rospy.Subscriber(
            "/move_base/status",
            GoalStatus,
            self.statusCallback,
            queue_size = 1
        )

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
    
    ## @fn velCallback
    ## @brief 
    ## @param
    ## @return

    #==================================================
    def velCallback(
        self,
        data
    ):
        for i in range(len(data.name)):
            if data.name[i] == "turtlebot3_waffle":
                self.sub_val_data = data.twist[i]

                break

        return



    #==================================================
    
    ## @fn statusCallback
    ## @brief 
    ## @param
    ## @return

    #==================================================
    def statusCallback(
        self,
        data
    ):
        tmp_list = data.status_list
        statuses = []
        for tmp in tmp_list:
            statuses.append(tmp.status)
        self.sub_status_data = statuses

        return



    #==================================================
    
    ## @fn setGoalPointMeter
    ## @brief 
    ## @param
    ## @return

    #==================================================
    def setGoalPointMeter(
        self,
        gpm
    ):
        self.goal_point_meter = gpm

        return


    #==================================================
    
    ## @fn getGoalPointMeter
    ## @brief 
    ## @param
    ## @return

    #==================================================
    def getGoalPointMeter(
        self,
    ):

        return self.goal_point_meter



    #==================================================
    
    ## @fn sendRotationGoal
    ## @brief move_baseで回転する関数
    ## @param
    ## @return
    ## @TODO 回転時の位置合わせを行っている時のロボットの動作が不自然

    #==================================================
    def sendRotationGoal(
        self,
        rad,
        position_meter_x,
        position_meter_y
    ):
        goal = MoveBaseGoal()
        q = tf.transformations.quaternion_from_euler(0, 0, rad)
        goal.target_pose.header.stamp = rospy.Time.now()
        goal.target_pose.header.frame_id = "map"
        goal.target_pose.pose.position.x = position_meter_x
        goal.target_pose.pose.position.y = position_meter_y
        goal.target_pose.pose.orientation.x = q[0]
        goal.target_pose.pose.orientation.y = q[1]
        goal.target_pose.pose.orientation.z = q[2]
        goal.target_pose.pose.orientation.w = q[3]

        self.client.send_goal(goal)

        return



    #==================================================
    
    ## @fn sendRotationTwist
    ## @brief cmd_velで最短角度の回転をする関数
    ## @param
    ## @return

    #==================================================
    def sendRotationTwist(
        self,
        rad,
        rad_now,
        speed = math.pi / 2
    ):
        # 回転時間
        rot_rad = abs(rad - rad_now)
        # 最短角度で回転する時間を決定
        if rot_rad < math.pi:
            target_time = rot_rad / speed
        else:
            target_time = (2.0*math.pi - rot_rad) / speed

        # Twist 型のデータ
        t = Twist()
        t.linear.x = 0
        # 最短角度で回転する方向を決定
        if 0 < rad - rad_now:
            if rot_rad < math.pi: 
                t.angular.z = speed
            else:
                t.angular.z = speed * -1
        else:
            if rot_rad < math.pi: 
                t.angular.z = speed * -1
            else:
                t.angular.z = speed

        # 開始の時刻を保存
        start_time = rospy.Time.now().to_sec()
        # 経過した時刻を取得
        end_time = rospy.Time.now().to_sec()

        # target_time を越えるまで走行
        rate = rospy.Rate(30)
        while end_time - start_time <= target_time:
            self.pub_vel.publish(t)
            end_time = rospy.Time.now().to_sec()
            rate.sleep()
        else:
            t = Twist()
            t.linear.x = 0
            t.angular.z = 0
            self.pub_vel.publish(t)

        print("rotation end")


        return



    #==================================================
    
    ## @fn sendPixelGoal
    ## @brief move_baseで移動する関数
    ## @param destination_pixel ロボットの進行座標（目的地）
    ## @param point_now_ ロボットの現在地点
    ## @param origin_meter_ マップ座標上のスタート地点
    ## @param resolution マップの粒度
    ## @return

    #==================================================
    def sendPixelGoal(
        self,
        destination_pixel,
        origin_meter_x,
        origin_meter_y,
        position_pixel_x,
        position_pixel_y,
        resolution
    ):
        goal = MoveBaseGoal()
        print("destination_pixel = {}".format(destination_pixel))
        e = math.atan2(position_pixel_x - destination_pixel[0], position_pixel_y - destination_pixel[1])
        q = tf.transformations.quaternion_from_euler(0, 0, e)
        goal.target_pose.header.stamp = rospy.Time.now()
        goal.target_pose.header.frame_id = "map"
        goal.target_pose.pose.position.x = origin_meter_y - destination_pixel[1] * resolution
        goal.target_pose.pose.position.y = origin_meter_x - destination_pixel[0] * resolution
        goal.target_pose.pose.orientation.x = q[0]
        goal.target_pose.pose.orientation.y = q[1]
        goal.target_pose.pose.orientation.z = q[2]
        goal.target_pose.pose.orientation.w = q[3]

        self.client.send_goal(goal)

        return



    #==================================================
    
    ## @fn sendMeterGoal
    ## @brief move_baseで移動する関数
    ## @param destination_pixel ロボットの進行座標（目的地）
    ## @param rad ロボットのゴール後の回転角度
    ## @return

    #==================================================
    def sendMeterGoal(
        self,
        destination_meter,
        rad
    ):
        goal = MoveBaseGoal()
        print("destination_meter = {}".format(destination_meter))
        #e = math.atan2(position_meter[0] - destination_meter[0], position_meter[1] - destination_meter[1])
        e = rad
        q = tf.transformations.quaternion_from_euler(0, 0, e)
        goal.target_pose.header.stamp = rospy.Time.now()
        goal.target_pose.header.frame_id = "map"
        goal.target_pose.pose.position.x = destination_meter[0]
        goal.target_pose.pose.position.y = destination_meter[1]
        goal.target_pose.pose.orientation.x = q[0]
        goal.target_pose.pose.orientation.y = q[1]
        goal.target_pose.pose.orientation.z = q[2]
        goal.target_pose.pose.orientation.w = q[3]

        self.client.send_goal(goal)

        wait = self.client.wait_for_result()

        if not wait:
            rospy.logerr("Action server not available!")
            rospy.signal_shutdown("Action server not available!")


        return



    #==================================================
    
    ## @fn subNaviStatus
    ## @brief ナビのステータスを確認する関数
    ## @param 
    ## @return

    #==================================================
    def subNaviStatus(
        self
    ):

        return self.sub_status_data



    #==================================================
    
    ## @fn sendDistanceTwist
    ## @brief cmd_velで一定距離を前進する関数
    ## @param
    ## @return

    #==================================================
    def sendDistanceTwist(
        self,
        pos,
        pos_now,
        speed = 0.3
    ):
        # 直進時間
        target_time = math.sqrt((pos[0] - pos_now[0])**2 + (pos[1] - pos_now[1])**2) / speed

        # Twist 型のデータ
        t = Twist()
        t.linear.x = speed
        t.angular.z = 0

        # 開始の時刻を保存
        start_time = rospy.Time.now().to_sec()
        # 経過した時刻を取得
        end_time = rospy.Time.now().to_sec()

        # target_time を越えるまで走行
        rate = rospy.Rate(30)
        while end_time - start_time <= target_time:
            self.pub_vel.publish(t)
            end_time = rospy.Time.now().to_sec()
            rate.sleep()
        else:
            t = Twist()
            t.linear.x = 0
            t.angular.z = 0
            self.pub_vel.publish(t)

        print("go distance end")

        return



    #==================================================
    
    ## @fn sendRunTwist
    ## @brief cmd_velで一定の角速度・速度で走行し続ける関数
    ## @param
    ## @return

    #==================================================
    def sendRunTwist(
        self,
        rad,
        rad_now,
        lin_speed = 0.3,
        rad_speed = math.pi / 45.0,
        target_time = -1.0
    ):
        # 回転時間
        rot_rad = abs(rad - rad_now)

        # Twist 型のデータ
        t = Twist()
        t.linear.x = lin_speed
        # 最短角度で回転する方向を決定
        if 0 < rad - rad_now:
            if rot_rad < math.pi: 
                t.angular.z = rad_speed
            else:
                t.angular.z = rad_speed * -1
        else:
            if rot_rad < math.pi: 
                t.angular.z = rad_speed * -1
            else:
                t.angular.z = rad_speed

        # 走行
        self.pub_vel.publish(t)

        # 時間が指定されていたら
        if target_time != -1.0:
            # 開始の時刻を保存
            start_time = rospy.Time.now().to_sec()
            # 経過した時刻を取得
            end_time = rospy.Time.now().to_sec()
            # target_time を越えるまで走行
            rate = rospy.Rate(30)
            while end_time - start_time <= target_time:
                end_time = rospy.Time.now().to_sec()
                rate.sleep()
            else:
                t = Twist()
                t.linear.x = 0
                t.angular.z = 0
                self.pub_vel.publish(t)

        return



    #==================================================
    
    ## @fn rotateToNearestInfRad
    ## @brief 一番近いInfradに向かって回転だけする関数
    ## @param 
    ## @return

    #==================================================
    def rotateToNearestInfRad(
        self,
        inf_rad_sorted,
        position_meter_x,
        position_meter_y,
        rad
    ):
        self.client.cancel_goal()

        # 現在向いている方角から最も近い方角を探す
        rad_temp = math.pi + rad
        for i in range(len(inf_rad_sorted)):
            if math.cos(inf_rad_sorted[i] - rad) > math.cos(rad_temp - rad):
                rad_temp = inf_rad_sorted[i]

        # 探索した方角へ回転＆回転終了まで待機
        # tip. 回転角度は相対ではなく絶対
        self.send_rotation_goal(rad_temp, position_meter_x, position_meter_y)



    #==================================================
    
    ## @fn cancelGoal
    ## @brief 
    ## @param 
    ## @return

    #==================================================
    def cancelGoal(
        self
    ):
        self.client.cancel_goal()

        return




    #==================================================
    
    ## @fn checkRobotInMargin
    ## @brief 目的地の一定範囲内（マージン）にロボットが存在するかを確認する関数
    ## @param 
    ## @return

    #==================================================
    def checkRobotInMargin(
        self,
        destination_meter,
        position_meter_x,
        position_meter_y,
        margin = 0.3
    ):
        dis_x = destination_meter[0] - position_meter_x
        dis_y = destination_meter[1] - position_meter_y

        dis = math.sqrt(dis_x**2 + dis_y**2)

        if dis < margin:
            
            return True

        else:

            return False



    #==================================================
    
    ## @fn getRobotVel
    ## @brief ロボットの速度を取得する関数
    ## @param 
    ## @return

    #==================================================
    def getRobotVel(
        self
    ):
        robot_vel_linear = self.sub_val_data.linear
        robot_vel = math.sqrt(robot_vel_linear.x**2 + robot_vel_linear.y**2 + robot_vel_linear.z**2)
        
        return robot_vel



    #==================================================
    
    ## @fn randomChoices
    ## @brief random.choicesを自分で実装したやつ
    ## @param population 重み付きの抽選を行われるリスト
    ## @param weight 重み
    ## @return

    #==================================================
    def randomChoices(
        self,
        population,
        weight
    ):
        np_w = np.array(weight)
        opp = 0
        # 最小値がゼロ以下なら、下駄oppを履かせる(最小値が１となる)
        if np.min(np_w) <= 0:
            opp = abs(np.min(np_w)) + 1
            np_w += opp

        upp = np.sum(np_w)
        rnd = random.randint(0, upp-1)
        inc = 0

        for i in range(len(np_w)):
            inc += np_w[i]
            if rnd < inc:
                
                return population[i]


    #==================================================
    
    ## @fn resetTrial
    ## @brief トライアルをもう一回やり直す関数
    ## @param
    ## @return

    #==================================================
    def resetTrial(
        self,
    ):
        # amclをキル
        os.system("rosnode kill /amcl")
        sleep(5.0)
        
        # map_serverをキル
        nodes = os.popen("rosnode list").readlines()
        for i in range(len(nodes)):
            nodes[i] = nodes[i].replace("\n","")
        for node in nodes:
            if "map_server" in node:
                os.system("rosnode kill " + node)
                sleep(5.0)    
        
        # move_baseをキル
        os.system("rosnode kill /move_base")
        sleep(5.0)

        # シミュレータをリセット
        print("reset_simulation")
        rospy.wait_for_service('/gazebo/reset_simulation')
        reset_world = rospy.ServiceProxy('/gazebo/reset_simulation', Empty)
        reset_world()
        print("reset_simulation end")
        sleep(5.0)

        """
        safe_node_list = ["/gazebo", "/gazebo_gui", "/rosout", "/rviz", "/robot_state_publisher", "/sm_search_maze_node"]
        nodes = os.popen("rosnode list").readlines()
        for i in range(len(nodes)):
            nodes[i] = nodes[i].replace("\n","")
        for node in nodes:
            if node in safe_node_list:
                continue
            else:
                os.system("rosnode kill " + node)
                sleep(5.0)
        """

        # 位置合わせのためにgmappingを起動する
        cmd = 'roslaunch turtlebot3_slam turtlebot3_gmapping.launch'
        Popen(cmd.split(" "))
        sleep(5.0)
        # 位置合わせできたらGmappingをキル
        os.system("rosnode kill /turtlebot3_slam_gmapping")
        sleep(5.0)
        
        # move_baseを復活
        cmd = 'roslaunch turtlebot3_navigation move_base.launch model:=waffle move_forward_only:=false'
        Popen(cmd.split(" "))
        sleep(5.0)

        # amclを復活
        cmd = 'roslaunch turtlebot3_navigation amcl.launch'
        Popen(cmd.split(" "))
        sleep(5.0)

        #rospy.sleep(60.0) # エラーが起きる（ROSTimeMovedBackwardsException: ROS time moved backwards）
        
        
        """
        # cmd = 1, means reset gmapping
        # cmd = 2, means to query the status of gmapping
        # status = 0, indicating that gmapping is not running
        # status = 1, means gmapping is running
        print("slam_cmd_srv")
        rospy.wait_for_service('/slam_cmd_srv')
        reset_map = rospy.ServiceProxy('/slam_cmd_srv', SlamCmd)
        reset_map(1)
        print("slam_cmd_srv end")

        sleep(5.0)
        """

        return


    #==================================================
    
    ## @fn exitTrial
    ## @brief トライアルを終了するためにメインノード以外のノードをキルする関数
    ## @param
    ## @return

    #==================================================
    def exitTrial(
        self,
    ):
        safe_node_list = ["/gazebo", "/gazebo_gui", "/rosout", "/rviz", "/robot_state_publisher", "/sm_search_maze_node"]
        nodes = os.popen("rosnode list").readlines()
        for i in range(len(nodes)):
            nodes[i] = nodes[i].replace("\n","")
        for node in nodes:
            if node in safe_node_list:
                continue
            else:
                os.system("rosnode kill " + node)

        sleep(5.0)


    #==================================================
    
    ## @fn changeMazeModel
    ## @brief 
    ## @param
    ## @return

    #==================================================
    def changeMazeModel(
        self,
        exp_cnt
    ):
        model_path = "/home/nakken/ros_ws/res_ws/src/tb3_pkgs/turtlebot3_simulations/turtlebot3_gazebo/models"
        model = QTABLE_DATA_LIST[exp_cnt][3]
        # モデルをMAZE7に変更する
        if model == "1":
            # MAZE7を召喚
            cmd = 'rosrun gazebo_ros spawn_model -file {}/turtlebot3_maze/maze_test7/model.sdf -sdf -model maze_test7 -y 0.0 -x 0.0'.format(model_path)
            Popen(cmd.split(" "))

            sleep(5.0)

            # MAZE8を墓地に
            cmd = 'rosservice call /gazebo/delete_model'
            Popen(cmd.split(" ") + ['model_name: "maze_test8"'])

            sleep(5.0)
        # モデルをMAZE8に変更する
        if model == "2":
            # MAZE8を召喚
            cmd = 'rosrun gazebo_ros spawn_model -file {}/turtlebot3_maze/maze_test8/model.sdf -sdf -model maze_test8 -y 0.0 -x 0.0'.format(model_path)
            Popen(cmd.split(" "))

            sleep(5.0)

            # MAZE7を墓地に
            cmd = 'rosservice call /gazebo/delete_model'
            Popen(cmd.split(" ") + ['model_name: "maze_test7"'])

            sleep(5.0)

            
