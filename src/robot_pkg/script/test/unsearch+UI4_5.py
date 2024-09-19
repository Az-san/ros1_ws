#!/usr/bin/python
# coding: UTF-8

import rospy
import cv2
import tf
import numpy as np
import math
import random
import actionlib
from nav_msgs.msg import *
from geometry_msgs.msg import *
from sensor_msgs.msg import LaserScan
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from time import sleep
from std_msgs.msg import Int16
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError

import pygame
from pygame.locals import *
import sys, os

import Queue

from map_laser_read1kai_def import *

#SCREEN_SIZE = (480, 270)
SCREEN_SIZE = (960, 540)
#SCREEN_SIZE = (1920, 1080)
TITLE, CHK_IS, CHK_BACK, WAIT_TURN_BACK, WAIT_5_SEC, ROBOT_JUDGE, HUMAN_JUDGE, TURN_IS, CONF_MOVE, WAIT_TURN_IS, GO_TO_UXP_IS, GO_TO_INF_IS, ESCAPE_IS, WAIT_TURN_INF, GO_TO_UXP_WHOLE_MAP, CHK_ROBOT_DEG_WHOLE_MAP, ESCAPE_IS_WHOLE_MAP, CHK_IS_AND_GOAL_WHOLE_MAP, HUMAN_ERROR, CONF_TRANS, CONF_MOVE_WHOLE_MAP = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20)
PLAY_UP_MENU, PLAY_DOWN_MENU, QUIT_MENU = (0, 1, 2)                 # （TITLE）メニュー項目
UP_WARD, DOWN_WARD, RESET = (0, 1, 2)         # （PLAY）俯瞰、仰瞰、リセットの変更
ESC, D, Q, R, W, M, I, Le, Ri, St, Ba = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

SUB_NAME = "miss"



class SearchUnexpField():
  def __init__(self):
    self.listener = tf.TransformListener()
    self.bridge = CvBridge()
    self.client = actionlib.SimpleActionClient('move_base', MoveBaseAction)
    self.sub1 = rospy.Subscriber("map", OccupancyGrid, self.mapCallback)
    self.sub2 = rospy.Subscriber('scan', LaserScan, self.laserCallback)
#    self.sub3 = rospy.Subscriber("/camera/rgb/image_raw", Image, self.imageCallback)
    self.sub4 = rospy.Subscriber("human_command", Int16, self.commandCallback)

    self.pub1 = rospy.Publisher('cmd_vel', Twist, queue_size=1)
    self.pub2 = rospy.Publisher('intersection_flag_robot', Int16, queue_size=1)
    self.pub3 = rospy.Publisher('robot_state', Int16, queue_size=1)

    # laserCallback
    self.inf_deg = []
    self.ahead_distance = 0

    # mapCallback
    size_map = 1, 1, 1
    size_img = 1, 1, 3
    self.map_out_comp = np.zeros(size_map, dtype=np.int8)
    self.img_out_comp = np.zeros(size_img, dtype=np.uint8)
    self.resolution = 1
    self.origin_pixel_x = 0
    self.origin_pixel_y = 0
    self.origin_meter_x = 0.0
    self.origin_meter_y = 0.0

    # imageCallback
    self.robot_view_img = np.zeros(size_img, dtype=np.uint8)
    self.robot_view_img_display = Queue.Queue()

    # commandCallback
    self.usr_command = -1
    self.get_key_flag = False
    self.get_hat_flag1 = False
    self.get_hat_flag2 = False

    # searchUnexp
    self.sight = 20

    # goToNearestUxp
    self.nearest_border_points_cog_temp = []

    # ゲームパットの初期化
    pygame.joystick.init()
    try:
      self.j = pygame.joystick.Joystick(0) # create a joystick instance
      self.j.init() # init instance
      print 'Joystickの名称: ' + self.j.get_name()
      print 'ボタン数 : ' + str(self.j.get_numbuttons())
    except pygame.error:
      print 'Joystickが見つかりませんでした。'

    # pygameの初期化
    pygame.init()

    # video capture
    #fourcc = cv2.VideoWriter_fourcc(*'MP4V')
    #self.out = cv2.VideoWriter('capture_exp.mp4',fourcc, 20.0, (960, 540))



  def laserCallback(self,data): # ロボットの進行方向を決定する
    inf_deg_temp = []
    ranges = data.ranges


    inf_deg_temp = getLaserInfDeg(data)
    self.inf_deg = inf_deg_temp                       # LRFが無限遠に行った方向（rad）
    self.ahead_distance = (ranges[0] + ranges[-1])/2  # ロボット前方の障害物との距離（ｍ）

#    print(self.ahead_distance)



  def mapCallback(self,data): # マップ情報を更新する

    data_height = data.info.height
    data_width = data.info.width
    self.resolution = data.info.resolution


    # 未探索地域の発見に使うマップ情報
    size_map = data_width, data_height, 1
    map_out = np.zeros(size_map, dtype=np.int8)
    # 表示に使うマップ情報
    size_img = data_width, data_height, 3
    img_out = np.zeros(size_img, dtype=np.uint8)


    # ディレイ発生源でした〜
    for y in range(data_height):
      for x in range(data_width):
        i = (data_width - x - 1) + (data_height - y - 1)* data_width
        intensity_map = 1
        intensity_img = (205,205,205)
        if data.data[i] == 0:
          intensity_map = 3
          intensity_img = (255,255,255)
        elif data.data[i] > 0:
          intensity_map = 2
          intensity_img = (0,0,0)
        map_out[x][y] = intensity_map
        img_out[x][y] = intensity_img

    self.img_out_comp = img_out
    self.map_out_comp = map_out

    # origin マップ座標上のスタート地点(pixel)
    self.origin_pixel_x = int(data_height + data.info.origin.position.x/data.info.resolution)
    self.origin_pixel_y = int(data_width + data.info.origin.position.y/data.info.resolution)
    # origin マップ座標上のスタート地点(meter)
    self.origin_meter_x = data_height * data.info.resolution + data.info.origin.position.x
    self.origin_meter_y = data_width * data.info.resolution + data.info.origin.position.y


  """
  def imageCallback(self,data): # 映像情報の更新
    try:
      robot_view_img_temp = self.bridge.imgmsg_to_cv2(data, "bgr8")
    except CvBridgeError as e:
      print(e)

    robot_view_img_temp_re = cv2.resize(robot_view_img_temp, SCREEN_SIZE)

    self.robot_view_img = robot_view_img_temp_re
    #self.robot_view_img_display.put(robot_view_img_temp_re)
  """


  def commandCallback(self,data): # ユーザーコマンドの取得
    self.usr_command = data.data
    if self.usr_command < 7:
      self.get_key_flag = True
      #print("get key command...")
      #print(data.data)
    else:
      self.get_hat_flag1 = True
      #print("get hat command...")
      #print(data.data)



  def send_rotation_goal(self, deg, trans_0, trans_1):
    goal = MoveBaseGoal()
    q = tf.transformations.quaternion_from_euler(0, 0, deg)
    goal.target_pose.header.stamp = rospy.Time.now()
    goal.target_pose.header.frame_id = "/map"
    goal.target_pose.pose.position.x = trans_0
    goal.target_pose.pose.position.y = trans_1
    goal.target_pose.pose.orientation.x = q[0]
    goal.target_pose.pose.orientation.y = q[1]
    goal.target_pose.pose.orientation.z = q[2]
    goal.target_pose.pose.orientation.w = q[3]

    self.client.send_goal(goal)



  def send_pixel_goal(self, cog, point_now_x, point_now_y):
    goal = MoveBaseGoal()
    e = math.atan2(point_now_x - cog[0], point_now_y - cog[1])
    q = tf.transformations.quaternion_from_euler(0, 0, e)
    goal.target_pose.header.stamp = rospy.Time.now()
    goal.target_pose.header.frame_id = "/map"
    goal.target_pose.pose.position.x = self.origin_meter_y - cog[1] * self.resolution
    goal.target_pose.pose.position.y = self.origin_meter_x - cog[0] * self.resolution
    goal.target_pose.pose.orientation.x = q[0]
    goal.target_pose.pose.orientation.y = q[1]
    goal.target_pose.pose.orientation.z = q[2]
    goal.target_pose.pose.orientation.w = q[3]

    self.client.send_goal(goal)



  def goToNearestUxp(self):

    if len(self.nearest_border_points_cog_temp) == 0:

      border_points_cog = searchUnexpWholeMap(self.map_out_comp)

      point_now_x = self.point_now_x
      point_now_y = self.point_now_y
      nearest_distance = 1000000
      nearest_border_points_cog = []
      for i in range(len(border_points_cog)):
        distance = abs(border_points_cog[i][0] - point_now_x) + abs(border_points_cog[i][1] - point_now_y)
        if distance < nearest_distance:
          nearest_distance = distance
          nearest_border_points_cog = border_points_cog[i]

      self.nearest_border_points_cog_temp = nearest_border_points_cog


    else:
      print("I'm not arrival in Whole Map Uxp...")

    if len(self.nearest_border_points_cog_temp) != 0:

      self.send_pixel_goal(self.nearest_border_points_cog_temp, self.point_now_x, self.point_now_y)

    else:

      print("!!! completed UXP place !!!")
      print("restart_now...")
      # ログの書き込み
      with open("/home/natume-lab/nakamura/SUB_DATA/" + SUB_NAME + "/cmd_log_" + str(self.main_loop_count) + "_" + SUB_NAME + ".txt", mode='w') as f:
        for i in range(len(self.cmd_log)):
          f.write(self.cmd_log[i])
      self.client.cancel_goal()
      self.init_variable()
      self.game_state = TITLE
      print("writing log now...")
      self.main_loop_count += 1



  def goToNearestDeg(self, trans_0, trans_1, e2pi, inf_deg_sorted, inf_points):
    self.client.cancel_goal()
    point_now_x = int(self.origin_pixel_x - trans_1/self.resolution)
    point_now_y = int(self.origin_pixel_y - trans_0/self.resolution)

    # 現在向いている方角から最も近い方角を探す
    deg_temp = math.pi + e2pi
    for i in range(len(inf_deg_sorted)):
      if math.cos(inf_deg_sorted[i] - e2pi) > math.cos(deg_temp - e2pi):
        deg_temp = inf_deg_sorted[i]

    print("e2pi = " + str(e2pi))
    print("deg_temp = " + str(deg_temp))

    # 探索した方角へ回転＆回転終了まで待機
    # 回転角度は相対ではなく絶対だった！！！
    self.send_rotation_goal(deg_temp, trans_0, trans_1)


  """
  def recColorFromCam(self):

    red_count = 0
    robot_view_img_hsv = cv2.cvtColor(self.robot_view_img, cv2.COLOR_BGR2HSV_FULL)
    shape = robot_view_img_hsv.shape

    for i in range(0, shape[0], 9):
      for j in range(0, shape[1], 9):
        if robot_view_img_hsv[i][j][0] < 20 or robot_view_img_hsv[i][j][0] > 230:
          if robot_view_img_hsv[i][j][1] > 128:
            red_count += 1

    if red_count > 20000:

      return True

    else:

      return False
  """


  def searchUnexp(self):

    if self.game_state == TITLE:

      # ディスプレイノードに飛ばす
      self.pub3.publish(0)



    elif self.game_state == CHK_IS:

      # ディスプレイノードに飛ばす
      self.pub3.publish(1)

      # ループ管理(6fps)
      if self.count_searchUnexp_loop < 10:

        self.count_searchUnexp_loop += 1

        return

      else:

        self.count_searchUnexp_loop = 0


      self.inf_deg_sorted = []             # inf_degを昇順にソートしたもの
      self.inf_points = []                 # LRFが無限遠に達した方角（Rad）

      try:
        for i in range(len(self.inf_deg)):
          self.inf_deg_sorted.append((self.inf_deg[i] + self.e2pi)%(2*math.pi))
        self.inf_deg_sorted.sort()

        for j in range(len(self.inf_deg_sorted)):
          self.inf_points.append([int(self.point_now_x - 2.2 * math.sin(self.inf_deg_sorted[j])/self.resolution), int(self.point_now_y - 2.2 * math.cos(self.inf_deg_sorted[j])/self.resolution)])
      except:
        print("ing_deg read error...")

        return


      # 交差点を通り抜けられなかったら
      if self.could_not_esc_is_flag:
        print("#### I could not esc IS!")

        self.could_not_esc_is_flag = False

      # 交差点・障害物チェック
      elif len(self.inf_deg) >= 3:

        self.game_state = CHK_BACK
        print("CHK_BACK...")

        return


      elif 3 > len(self.inf_deg) > 0:

        if self.gpio_status == 1:
          #==============================================

          #         ラズパイに信号を出す。   (交差点ではないところ)

          #==============================================
          self.pub2.publish(0)

          self.gpio_status = 0


      elif len(self.inf_deg) == 0:

        if self.client.get_state() == 3:

#          print("====== sent <goToNearestUxp len of inf_deg = 0> goal ======")
#          self.goToNearestUxp()

#          self.game_state = GO_TO_UXP_WHOLE_MAP   #++++++++++++++++++++++++++++++++++++++++++
#          print("GO_TO_UXP_WHOLE_MAP...")         #++++++++++++++++++++++++++++++++++++++++++(2019/01/16)

          # InfがないときはマニュアルでNaviする
          self.game_state = CHK_IS   #++++++++++++++++++++++++++++++++++++++++++(2019/01/18)
          print("CHK_IS...")

          return


      else:

        print("Searching END...")        

        return



      if self.ahead_distance >= 2.5:

        for i in range(len(self.inf_deg_sorted)):

          # 前方にinf_pointがあるか確認
          dist_e2pi_inf_deg = self.inf_deg_sorted[i] - self.e2pi
          if math.cos(dist_e2pi_inf_deg) > 0.85:

#            print("====== sent <go to inf_point> goal ======")
#            print("go to deg<" + str(i) + ">, " + str(self.inf_deg_sorted[i]))

            self.send_pixel_goal(self.inf_points[i], self.point_now_x, self.point_now_y)

            break

        else:

          print("====== sent <goToNearestDeg for else> goal ======")
          self.goToNearestDeg(self.trans_0, self.trans_1, self.e2pi, self.inf_deg_sorted, self.inf_points)

          self.time_now = rospy.get_time()
          self.game_state = WAIT_TURN_INF

      else:
        if self.client.get_state() == 3:

          print("====== sent <goToNearestDeg elif arrival in dis > 2.5> goal ======")
          self.goToNearestDeg(self.trans_0, self.trans_1, self.e2pi, self.inf_deg_sorted, self.inf_points)

          self.time_now = rospy.get_time()
          self.game_state = WAIT_TURN_INF

        elif self.ahead_distance < 0.60:

          print("====== sent <goToNearestDeg elif arrival in dis < 0.60> goal ======")
          self.goToNearestDeg(self.trans_0, self.trans_1, self.e2pi, self.inf_deg_sorted, self.inf_points)

          self.time_now = rospy.get_time()
          self.game_state = WAIT_TURN_INF

        #else:

        #  print("ERROR! === CHK_IS")




    elif self.game_state == CHK_BACK:

      inf_deg = self.inf_deg
      inf_deg_ahead_ave_count = 0
      inf_deg_back_ave = 0
      inf_deg_back_ave_count = 0

      for i in range(len(inf_deg)):

        # 後方にinf_pointがあるか確認
        if math.cos(inf_deg[i]) > -0.3:

          inf_deg_ahead_ave_count += 1

        else:

          inf_deg_back_ave += inf_deg[i]
          inf_deg_back_ave_count += 1

      if inf_deg_back_ave_count > 1:

        self.inf_deg_sorted = []             # inf_degを昇順にソートしたもの
        self.inf_points = []                 # LRFが無限遠に達した方角（Rad）

        try:
          for i in range(len(inf_deg)):
            self.inf_deg_sorted.append((inf_deg[i] + self.e2pi)%(2*math.pi))
          self.inf_deg_sorted.sort()

          for j in range(len(self.inf_deg_sorted)):
            self.inf_points.append([int(self.point_now_x - 2.2 * math.sin(self.inf_deg_sorted[j])/self.resolution), int(self.point_now_y - 2.2 * math.cos(self.inf_deg_sorted[j])/self.resolution)])
        except:
          print("ing_deg read error...")

          return

        inf_deg_back_ave = (inf_deg_back_ave / inf_deg_back_ave_count) + self.e2pi
        self.send_rotation_goal(inf_deg_back_ave, self.trans_0, self.trans_1)

        self.find_points_back_flag = True
        self.game_state = WAIT_TURN_BACK
        print("WAIT_TURN_BACK...")

      else:
        # 5秒間マップを更新させた後、
        self.client.cancel_goal()
        self.time_now = rospy.get_time()

        self.game_state = WAIT_5_SEC
        print("//// judging the way... 5 seconds ////")



    elif self.game_state == WAIT_TURN_BACK:

      if self.client.get_state() == 3:

        self.client.cancel_goal()
        self.time_now = rospy.get_time()
        #self.turn_back_flag = True

        self.game_state = WAIT_5_SEC
        print("//// judging the way... 5 seconds ////")




    elif self.game_state == WAIT_5_SEC:

      # ディスプレイノードに飛ばす
      self.pub3.publish(2)

      if rospy.get_time() - self.time_now >= 5.0:

        self.get_hat_flag2 = False

        self.game_state = ROBOT_JUDGE
        print("ROBOT_JUDGE...")



    elif self.game_state == ROBOT_JUDGE:

      inf_deg = self.inf_deg
      if len(inf_deg) >= 3:

        if self.find_points_back_flag == False:

          self.inf_deg_sorted = []             # inf_degを昇順にソートしたもの
          self.inf_points = []                 # LRFが無限遠に達した方角（Rad）

          try:
            for i in range(len(inf_deg)):
              self.inf_deg_sorted.append((inf_deg[i] + self.e2pi)%(2*math.pi))
            self.inf_deg_sorted.sort()

            for j in range(len(self.inf_deg_sorted)):
              self.inf_points.append([int(self.point_now_x - 2.2 * math.sin(self.inf_deg_sorted[j])/self.resolution), int(self.point_now_y - 2.2 * math.cos(self.inf_deg_sorted[j])/self.resolution)])
          except:
            print("ing_deg read error...")

            return

        else:

          self.find_points_back_flag == False


      # inf_points周りの未探索地域を探す
      self.unexp_points, self.unexp_deg_sorted = searchUnexpAroundPoint(self.map_out_comp, self.inf_points, self.inf_deg_sorted, self.sight)

      self.trans_0_now = self.trans_0     # 現在地点のセーブ
      self.trans_1_now = self.trans_1     # 現在地点のセーブ
      self.e2pi_now = self.e2pi           # 現在角度のセーブ

      if len(self.unexp_points) != 0:

        self.find_uxp_flag = True
        # 進行方向をランダムに選択
        self.random_go_unexp_num = int(random.random() * 100) % len(self.unexp_points)
        # 全体マップ参照時にUXPを見つけたら、WholeMapUXPはリセットする。
        self.nearest_border_points_cog_temp = []


        print("len of unexp_points = " + str(len(self.unexp_points)))
        print("random_go_unexp_num = " + str(self.random_go_unexp_num))


        # ロボットの向いている方角から進行方向を左右にクラス分け(学習データ用)
        #self.cmd_id += 1
        self.robot_dir = ""

        inf_deg_sorted = self.inf_deg_sorted
        inf_points = self.inf_points
        inf_directions = []

        if len(self.unexp_points) != 0:
          print("selected unexp...")
          """
          unexp_deg_e2pi_dif = self.unexp_deg_sorted[self.random_go_unexp_num] - self.e2pi
          if math.cos(unexp_deg_e2pi_dif) > 0.85:
            self.robot_dir = "S"
          elif math.sin(unexp_deg_e2pi_dif) > 0.50:
            self.robot_dir = "L"
          elif math.sin(unexp_deg_e2pi_dif) < -0.50:
            self.robot_dir = "R"
          else:
            self.robot_dir = "B"
          """

          # 現在向いている方角から最も遠い方角を探す（ロボット後方のinfを探す）
          # 上下左右反転注意！！！！！！！！！！！！！！！！！！
          inf_deg_farthest_to_e2pi = 0 + self.e2pi
          for i in range(len(inf_deg_sorted)):
            if math.cos(inf_deg_sorted[i] - self.e2pi) < math.cos(inf_deg_farthest_to_e2pi - self.e2pi):
              inf_deg_farthest_to_e2pi = inf_deg_sorted[i]
          #print("inf_deg_farthest_to_e2pi = " + str(inf_deg_farthest_to_e2pi))
          #print("#######################")
          print("selected inf...")
          #inf_deg_e2pi_dif = self.inf_deg_sorted[i] - self.e2pi
          unexp_deg_e2pi_dif = self.unexp_deg_sorted[self.random_go_unexp_num] - inf_deg_farthest_to_e2pi
          #print("inf_deg_sorted = " + str(self.inf_deg_sorted[i]))
          #print("inf_deg_e2pi_dif = " + str(inf_deg_e2pi_dif))
          if math.cos(unexp_deg_e2pi_dif) < -0.88:
            self.robot_dir = "S"
          elif math.cos(unexp_deg_e2pi_dif) > 0.88:
            self.robot_dir = "B"
          elif math.sin(unexp_deg_e2pi_dif) < -0.40:
            self.robot_dir = "L"
          elif math.sin(unexp_deg_e2pi_dif) > 0.40:
            self.robot_dir = "R"

        print("#####dir class = " + self.robot_dir)

        # ゲームパッドで人間に意思表示させる
        # Key_commandでステートを遷移させる
        self.game_state = HUMAN_JUDGE
        print("HUMAN_JUDGE...")


      # 交差点でUxpがなかったら、最近傍のUnexpへナビゲーションする。
      else:

        #self.get_hat_flag2 = False
        self.find_uxp_flag = False
        self.game_state = HUMAN_JUDGE
        print("HUMAN_JUDGE...")



    elif self.game_state == HUMAN_JUDGE:

      # ディスプレイノードに飛ばす
      self.pub3.publish(3)

      if self.get_hat_flag2 == True:

        # ディスプレイノードに飛ばす
        self.pub3.publish(1)

        tmp_random = int((random.random() * 100))
        # 人のジャッジとロボットのジャッジどちらの進行方向に進むかランダム（０：ロボット、１：ヒト）
        self.random_human_or_robot_num = tmp_random % 2
        #self.random_human_or_robot_num = 0 #++++++++++++++++++++++++++(20190205パワポ素材用に変えました)
        print("randm answer is " + str(tmp_random))
        print("judge answer is " + str(self.random_human_or_robot_num))

        if self.random_human_or_robot_num == 0:
          print("select ROBOT judge by chance...")
        else:
          print("select HUMAN judge by chance...")

        ##############################


        inf_deg_sorted = self.inf_deg_sorted
        inf_points = self.inf_points
        inf_directions = []

        print("inf_deg_sorted" + str(inf_deg_sorted))
        print("self.e2pi" + str(self.e2pi))

        if len(inf_deg_sorted) != 0:

          # 現在向いている方角から最も遠い方角を探す（ロボット後方のinfを探す）
          # 上下左右反転注意！！！！！！！！！！！！！！！！！！
          inf_deg_farthest_to_e2pi = 0 + self.e2pi
          for i in range(len(inf_deg_sorted)):
            if math.cos(inf_deg_sorted[i] - self.e2pi) < math.cos(inf_deg_farthest_to_e2pi - self.e2pi):
              inf_deg_farthest_to_e2pi = inf_deg_sorted[i]
          #print("inf_deg_farthest_to_e2pi = " + str(inf_deg_farthest_to_e2pi))
          #print("#######################")
          print("selected inf...")
          for i in range(len(inf_deg_sorted)):
            #inf_deg_e2pi_dif = self.inf_deg_sorted[i] - self.e2pi
            inf_deg_e2pi_dif = self.inf_deg_sorted[i] - inf_deg_farthest_to_e2pi
            #print("inf_deg_sorted = " + str(self.inf_deg_sorted[i]))
            #print("inf_deg_e2pi_dif = " + str(inf_deg_e2pi_dif))
            if math.cos(inf_deg_e2pi_dif) < -0.88:
              inf_directions.append("S")
            elif math.cos(inf_deg_e2pi_dif) > 0.88:
              inf_directions.append("B")
            elif math.sin(inf_deg_e2pi_dif) < -0.40:
              inf_directions.append("L")
            elif math.sin(inf_deg_e2pi_dif) > 0.40:
              inf_directions.append("R")

          print("self.human_dir = " + str(self.human_dir))
          print("inf_directions = " + str(inf_directions))

          for i in range(len(inf_directions)):
            if self.human_dir == inf_directions[i]:

              break

          else:
            print("there are no direction which you judged...")

            self.cmd_dir = "human_mistake"
            self.cmd_log.append(str(self.cmd_id) + "," + "?" + "," + "?" + "," + self.cmd_dir + "\n")

            self.game_state = HUMAN_ERROR
            self.time_now = rospy.get_time()
            print("HUMAN_ERROR...")

            return

        else:
          print("there are no inf_deg_sorted...")

          self.get_deg_wholemap_flag = True
          self.game_state = GO_TO_UXP_WHOLE_MAP
          print("GO_TO_UXP_WHOLE_MAP...")

          return

        ##############################

        if self.random_human_or_robot_num == 0:

          if self.find_uxp_flag:

            self.cmd_dir = "robot"
            self.cmd_log.append(str(self.cmd_id) + "," + self.human_dir + "," + self.robot_dir + "," + self.cmd_dir + "\n")

            self.game_state = TURN_IS
            print("TURN_IS...")

          else:

            self.get_deg_wholemap_flag = True
            self.game_state = GO_TO_UXP_WHOLE_MAP
            print("GO_TO_UXP_WHOLE_MAP...")

        else:

            ##############################

            self.cmd_dir = "human"
            self.cmd_log.append(str(self.cmd_id) + "," + self.human_dir + "," + self.robot_dir + "," + self.cmd_dir + "\n")

            self.human_judge_inf_point = inf_points[i]
            self.human_judge_inf_deg_sorted = inf_deg_sorted[i]
            print("human go to " + self.human_dir + " direction...")

            self.game_state = TURN_IS
            print("TURN_IS...")

            ##############################



    elif self.game_state == HUMAN_ERROR:

      # ディスプレイノードに飛ばす
      self.pub3.publish(4)

      if rospy.get_time() - self.time_now >= 3.0:

        self.client.cancel_goal()
        self.get_hat_flag2 = False

        self.game_state = WAIT_5_SEC #++++++++++++++++++++++++++++++++
        print("WAIT_5_SEC...") #++++++++++++++++++++++++++++++++++++++(2019/01/18)




    elif self.game_state == TURN_IS:

      if self.random_human_or_robot_num == 0:
        # ロボットが決定した方向に旋回する
        if len(self.unexp_points) != 0:
          self.send_rotation_goal(self.unexp_deg_sorted[self.random_go_unexp_num], self.trans_0, self.trans_1)
      else:
        # ヒトが決定した方向に旋回する
        if len(self.inf_points) != 0:
          self.send_rotation_goal(self.human_judge_inf_deg_sorted, self.trans_0, self.trans_1)
      """
      if self.gpio_status == 0:
        #==============================================

        #         ラズパイに信号を出す。   (交差点で曲がった瞬間)----------------------(2019/01/20)

        #==============================================
        self.pub2.publish(1)

        self.gpio_status = 1
      """
      self.get_hat_flag2 = False

      self.time_now_debug = rospy.get_time()

      self.game_state = WAIT_TURN_IS
      print("WAIT_TURN_IS...")

#      self.game_state = CONF_MOVE
#      print("CONF_MOVE...")




      """
    elif self.game_state == CONF_MOVE:

      print("e360 = " + str(self.e360))

      if self.cmd_dir == "R" or self.cmd_dir == "L":
        if math.cos(self.e2pi_now - self.e2pi) < 0.999:

          print("delay = " + str(rospy.get_time() - self.time_now_debug))

          if self.gpio_status == 0:
            #==============================================

            #         ラズパイに信号を出す。   (交差点で曲がった瞬間)

            #==============================================
            self.pub2.publish(1)

            self.gpio_status = 1


          self.cmd_dir = ""
          self.game_state = WAIT_TURN_IS
          print("WAIT_TURN_IS for LR...")

      elif self.cmd_dir == "B" or self.cmd_dir == "S":
        # ５センチ動いたらTTL++++++++++++++++++++++++++++++++(2019/01/20)
        if abs(math.sqrt(self.trans_0_now*self.trans_0_now + self.trans_1_now*self.trans_1_now) - math.sqrt(self.trans_0*self.trans_0 + self.trans_1*self.trans_1)) > 0.05:

          print("delay = " + str(rospy.get_time() - self.time_now_debug))

          if self.gpio_status == 0:
            #==============================================

            #         ラズパイに信号を出す。   (交差点で曲がった瞬間)

            #==============================================
            self.pub2.publish(1)

            self.gpio_status = 1


          self.cmd_dir = ""
          self.game_state = WAIT_TURN_IS
          print("WAIT_TURN_IS for BS...")


      else:

        print("delay = " + str(rospy.get_time() - self.time_now_debug))

        self.game_state = WAIT_TURN_IS
        print("WAIT_TURN_IS for else...")
      """


    elif self.game_state == WAIT_TURN_IS:

      if self.client.get_state() == 3:

        if self.random_human_or_robot_num == 0:
          # ロボットが決定した方向に移動する
          self.game_state = GO_TO_UXP_IS
          print("GO_TO_UXP_IS...")

        else:
          # ヒトが決定した方向に移動する
          self.game_state = GO_TO_INF_IS
          print("GO_TO_INF_IS...")

      # 3[deg]以上でTTL ++++++++++++++++++++++++++++++++++++++++++++++++(2019/01/20)
      elif math.cos(self.e2pi_now - self.e2pi) < 0.9986:

        if self.gpio_status == 0:
          #==============================================

          #         ラズパイに信号を出す。   (交差点で曲がった瞬間)

          #==============================================
          self.pub2.publish(1)

          self.gpio_status = 1

          print("delay_turn = " + str(rospy.get_time() - self.time_now_debug))



    elif self.game_state == WAIT_TURN_INF:

      if self.client.get_state() == 3:

        self.game_state = CHK_IS
        print("CHK_IS...")

      elif rospy.get_time() - self.time_now >= 15.0:

        print("###please move with manual...")

        self.game_state = CHK_IS
        print("CHK_IS...")



    elif self.game_state == GO_TO_UXP_IS:

      if len(self.unexp_points) != 0:

        print("====== sent <select intersection_unexp> goal ======")
#        print("go to deg<" + str(self.random_go_unexp_num) + ">, " + str(self.unexp_deg_sorted[self.random_go_unexp_num]))
        self.send_pixel_goal(self.unexp_points[self.random_go_unexp_num], self.point_now_x, self.point_now_y)

        self.time_now = rospy.get_time()
#        self.game_state = ESCAPE_IS #---------------------------------(2019/01/23)
#        print("ESCAPE_IS...")
        self.game_state = CONF_TRANS
        print("CONF_TRANS...")


    elif self.game_state == GO_TO_INF_IS:

      if len(self.inf_points) != 0:

        print("====== sent <select human_judge_inf_point> goal ======")
        self.send_pixel_goal(self.human_judge_inf_point, self.point_now_x, self.point_now_y)

        self.time_now = rospy.get_time()
#        self.game_state = ESCAPE_IS #---------------------------------(2019/01/20)
#        print("ESCAPE_IS...")
        self.game_state = CONF_TRANS
        print("CONF_TRANS...")



    elif self.game_state == CONF_TRANS: # +++++++++++++++++++++++++++++++(2019/01/20)

      # 4[cm]以上でTTL
      if math.sqrt((self.trans_0_now-self.trans_0)**2 + (self.trans_1_now-self.trans_1)**2) > 0.04:

        print("delay_dist = " + str(rospy.get_time() - self.time_now_debug))

        if self.gpio_status == 0:
          #==============================================

          #         ラズパイに信号を出す。   (交差点で曲がった瞬間)

          #==============================================
          self.pub2.publish(1)

          self.gpio_status = 1


        self.game_state = ESCAPE_IS
        print("ESCAPE_IS...")



    elif self.game_state == ESCAPE_IS:

      self.inf_deg_sorted = []             # inf_degを昇順にソートしたもの
      self.inf_points = []                 # LRFが無限遠に達した方角（Rad）

      try:
        for i in range(len(self.inf_deg)):
          self.inf_deg_sorted.append((self.inf_deg[i] + self.e2pi)%(2*math.pi))
        self.inf_deg_sorted.sort()

        for j in range(len(self.inf_deg_sorted)):
          self.inf_points.append([int(self.point_now_x - 2.2 * math.sin(self.inf_deg_sorted[j])/self.resolution), int(self.point_now_y - 2.2 * math.cos(self.inf_deg_sorted[j])/self.resolution)])
      except:
        print("ing_deg read error...")

        return
      """
      # 交差点を抜けたか？
      if self.turn_back_flag == True:
        if self.client.get_state() == 3:

          self.turn_back_flag = False

          self.game_state = CHK_IS
          print("CHK_IS...")

      else:
      """
      if len(self.inf_deg) < 3:

        self.game_state = CHK_IS
        print("CHK_IS...")

      elif rospy.get_time() - self.time_now >= 9.0:

        if len(self.inf_deg) >= 3:

          print("====== sent <goToNearestDeg for else> goal ======")
          self.goToNearestDeg(self.trans_0, self.trans_1, self.e2pi, self.inf_deg_sorted, self.inf_points)

          self.could_not_esc_is_flag = True
          self.time_now = rospy.get_time()
          self.game_state = WAIT_TURN_INF

          return

          """
          for i in range(len(self.inf_deg_sorted)):

            # 前方にinf_pointがあるか確認
            dist_e2pi_inf_deg = self.inf_deg_sorted[i] - self.e2pi
            if math.cos(dist_e2pi_inf_deg) > 0.85:

              self.send_pixel_goal(self.inf_points[i], self.point_now_x, self.point_now_y)

              self.game_state = ESCAPE_IS
              self.time_now = rospy.get_time()
              print("ESCAPE_IS...")

              return

          else:

            print("====== sent <goToNearestDeg for else> goal ======")
            self.goToNearestDeg(self.trans_0, self.trans_1, self.e2pi, self.inf_deg_sorted, self.inf_points)

            self.game_state = WAIT_TURN_INF

            return
          """
        self.game_state = CHK_IS
        print("CHK_IS...")



    elif self.game_state == GO_TO_UXP_WHOLE_MAP:

      # ディスプレイノードに飛ばす
      self.pub3.publish(1)

      self.time_now = rospy.get_time()
      self.get_hat_flag2 = False
      self.time_now_debug = rospy.get_time()

#      self.game_state = CHK_ROBOT_DEG_WHOLE_MAP # ---------------------------------------(2019/01/20)
#      print("CHK_ROBOT_DEG_WHOLE_MAP...")
      self.game_state = CONF_MOVE_WHOLE_MAP
      print("CONF_MOVE_WHOLE_MAP...")

      print("====== sent <goToNearestUxp len of uxp = 0> goal ======")
      self.goToNearestUxp()
      """
      if self.gpio_status == 0:
        #==============================================

        #         ラズパイに信号を出す。   (交差点で曲がった瞬間)---------------------------------------(2019/01/20)

        #==============================================
        self.pub2.publish(1)

        self.gpio_status = 1
      """


    # ver2 +++++++++++++++++++++++++++++++++++++++++++++(2019/01/20)
    elif self.game_state == CONF_MOVE_WHOLE_MAP:

      delay_cos = math.cos(self.e2pi_now - self.e2pi)
      delay_dist = math.sqrt((self.trans_0_now-self.trans_0)**2 + (self.trans_1_now-self.trans_1)**2)

      print("e360 = " + str(self.e360))
      print("dist = " + str(delay_dist))

      # 3[deg]以上、4[cm]以上でTTL
      if delay_cos < 0.9986 or delay_dist > 0.04:

        print("delay = " + str(rospy.get_time() - self.time_now_debug))

        if self.gpio_status == 0:
          #==============================================

          #         ラズパイに信号を出す。   (交差点で曲がった瞬間)

          #==============================================
          self.pub2.publish(1)

          self.gpio_status = 1


        self.game_state = CHK_ROBOT_DEG_WHOLE_MAP
        print("CHK_ROBOT_DEG_WHOLE_MAP...")



    elif self.game_state == CHK_ROBOT_DEG_WHOLE_MAP:

      if rospy.get_time() - self.time_now >= 7.0:

        # ロボットがこの時に交差点にいる場合
        if self.get_deg_wholemap_flag:
          # ロボットの向いている方角から進行方向を左右にクラス分け(学習データ用)
          #self.cmd_id += 1
          self.robot_dir = ""

          inf_deg_e2pi_dif = math.atan2(self.trans_1_now-self.trans_1, self.trans_0-self.trans_0_now) + self.e2pi
          #inf_deg_e2pi_dif = self.e2pi - self.e2pi_now
          print("deg_wholemap = " + str(inf_deg_e2pi_dif))

          if math.cos(inf_deg_e2pi_dif) > 0.90:
            self.robot_dir = "S"
          elif math.cos(inf_deg_e2pi_dif) < -0.90:
            self.robot_dir = "B"
          elif math.sin(inf_deg_e2pi_dif) > 0.34:
            self.robot_dir = "L"
          elif math.sin(inf_deg_e2pi_dif) < -0.34:
            self.robot_dir = "R"


          print("dir class = " + self.robot_dir)

          self.cmd_dir = "robot"
          self.cmd_log.append(str(self.cmd_id) + "," + self.human_dir + "," + self.robot_dir + "_chk_v" + "," + self.cmd_dir + "\n")

          self.get_deg_wholemap_flag = False

        self.game_state = ESCAPE_IS_WHOLE_MAP
        self.time_now = rospy.get_time()
        print("ESCAPE_IS_WHOLE_MAP...")



    elif self.game_state == ESCAPE_IS_WHOLE_MAP:

      if self.gpio_status == 1:
        #==============================================

        #         ラズパイに信号を出す。   (交差点ではないところ)++++++++++++++++++++(2019/01/16)

        #==============================================
        self.pub2.publish(0)

        self.gpio_status = 0

      # 交差点を抜けたか？
      if len(self.inf_deg) < 3:
      #if rospy.get_time() - self.time_now >= 7.0:

        self.game_state = CHK_IS_AND_GOAL_WHOLE_MAP
        print("CHK_IS_AND_GOAL_WHOLE_MAP...")

      elif self.client.get_state() == 3:

        self.game_state = CHK_IS_AND_GOAL_WHOLE_MAP
        print("CHK_IS_AND_GOAL_WHOLE_MAP...")




    elif self.game_state == CHK_IS_AND_GOAL_WHOLE_MAP:

      if len(self.inf_deg) >= 3:

        self.client.cancel_goal() #++++++++++++++++++++++++++++++++++++++++++++(2019/01/18)

        self.game_state = CHK_BACK
        print("CHK_BACK...")

      elif self.client.get_state() == 3:

        self.inf_deg_sorted = []             # inf_degを昇順にソートしたもの
        self.inf_points = []                 # LRFが無限遠に達した方角（Rad）

        try:
          for i in range(len(self.inf_deg)):
            self.inf_deg_sorted.append((self.inf_deg[i] + self.e2pi)%(2*math.pi))
          self.inf_deg_sorted.sort()

          for j in range(len(self.inf_deg_sorted)):
            self.inf_points.append([int(self.point_now_x - 2.2 * math.sin(self.inf_deg_sorted[j])/self.resolution), int(self.point_now_y - 2.2 * math.cos(self.inf_deg_sorted[j])/self.resolution)])
        except:
          print("ing_deg read error...")

          return

        self.nearest_border_points_cog_temp = []

        #self.game_state = CHK_IS
        #print("CHK_IS...")

        print("====== sent <goToNearestDeg for else> goal ======")
        self.goToNearestDeg(self.trans_0, self.trans_1, self.e2pi, self.inf_deg_sorted, self.inf_points)

        self.could_not_esc_is_flag = True
        self.time_now = rospy.get_time()
        self.game_state = WAIT_TURN_INF




  def init_variable(self):
    self.game_state = TITLE
    self.cur_menu = PLAY_UP_MENU
    self.view_mode = UP_WARD

    self.e360 = 0                 # ロボットの角度(deg)
    self.e2pi = 0                 # ロボットの角度(rad)
    self.trans_0 = 0              # ロボットの現在地（meter:ｘ）
    self.trans_1 = 0              # ロボットの現在地（meter:ｙ）
    self.point_now_x = 0          # ======#=======（Pixel:width）
    self.point_now_y = 0          # ======#=======（Pixel:height）

    self.count_searchUnexp_loop = 0
    self.inf_deg_sorted = []             # inf_degを昇順にソートしたもの
    self.unexp_deg_sorted = []
    self.inf_points = []                 # LRFが無限遠に達した方角（Rad）
    self.unexp_points = []               # LRFが無限遠に達し、かつ未探索地域である角度（Rad）
    self.human_judge_inf_point = []      # ヒトが決定した方向にあったinf_pointsの一つ
    self.human_judge_inf_deg_sorted = [] # ヒトが決定した方向にあったinf_deg_sortedの一つ
    self.time_now = 0.0
    self.time_now_debug = 0.0
    self.intersection_flag = False       # 交差点のフラグ
    self.ahead_distance_flag = False     # 前方0.55mに障害物があるフラグ
    self.escape_intersection = True      # 交差点を抜けだしたフラグ
    self.random_go_unexp_num = -1        # unexp_pointsからランダムに1つ選ぶ
    self.human_go_inf_num = -1          # inf_pointsからランダムに1つ選ぶ
    self.random_human_or_robot_num = -1
    self.gpio_status = 0                 # raspi3のGPIOのステータス
    self.len_inf_deg_pre = 100

    self.cmd_log = []                    # 人間がゲームパットで入力した方向と、ロボットが決定した方向を記録する
    self.cmd_log.append("id,human,robot,which? (left = L, right = R, straight = S, back = B)\n")
    self.cmd_id = 0                      # cmd記録用ID
    self.robot_dir = ""
    self.human_dir = ""
    self.cmd_dir = ""
    self.e2pi_now = 0                    # ロボットの動作検知用

    self.find_uxp_flag = True
    self.turn_back_flag = False
    self.could_not_esc_is_flag = False
    self.get_deg_wholemap_flag = False
    self.find_points_back_flag = False

    self.write_map_count = 0



  def main(self):
    #screen = pygame.display.set_mode(SCREEN_SIZE)
    #pygame.display.set_caption("UI")
    #self.load_images()            # 素材のロード
    self.main_loop_count = 0

    self.init_variable()
    """
    sysfont = pygame.font.SysFont(None, 30)
    self.wait_5_sec_txt1 = sysfont.render("I found a intersection.", True, (255,0,0), (255,255,0))
    self.wait_5_sec_txt2 = sysfont.render("Please wait 5 seconds.", True, (255,0,0), (255,255,0))
    self.human_judge_txt = sysfont.render("please determine which way do you go?", True, (255,0,0), (255,255,0))
    self.preparation_txt = sysfont.render("in preparation...", True, (255,0,0), (255,255,0))

    self.turn_txt_o = sysfont.render("o", True, (0,255,255))
    """
    clock = pygame.time.Clock()
    while True:

      # Robot
      try:
        (trans,rot) = self.listener.lookupTransform('/map', '/base_link', rospy.Time(0))
        e = tf.transformations.euler_from_quaternion((rot[0], rot[1], rot[2], rot[3]))


        # convert -pi < theta < pi TO 0 < theta < 360 and 0 < theta < 2pi
        self.e360 = 0
        if e[2] < 0:
          self.e2pi = 2*math.pi + e[2]
          self.e360 = ((2*math.pi + e[2])/math.pi) * 180
        else:
          self.e2pi = e[2]
          self.e360 = (e[2]/math.pi) * 180

        self.trans_0 = trans[0]
        self.trans_1 = trans[1]

        # point_now マップ上の現在地点
        self.point_now_x = int(self.origin_pixel_x - trans[1]/self.resolution)
        self.point_now_y = int(self.origin_pixel_y - trans[0]/self.resolution)


      except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
        print("TF reading ERROR...")
        pass

      #print("dist_from_orig = " + str(math.sqrt(self.trans_0*self.trans_0 + self.trans_0*self.trans_0)))

      # UI
      clock.tick(30)
      #screen.fill((205,205,205))
      #self.draw(screen)
      self.searchUnexp()

      #self.out.write(self.robot_view_img)

      #pygame.display.update()
      self.key_handler()




  """
  def draw(self, screen):


    if self.game_state == TITLE:

      # ドットを描画
      screen.blit(self.titleImg, self.title_rect)

    else:
      # 俯瞰視点モード
      if self.view_mode == UP_WARD:
        img_cv = self.img_out_comp
        img_cv = drawSearchingUnexp(img_cv,self.point_now_x,self.point_now_y,self.inf_points,self.unexp_points)
        img_cv = img_cv[:,:,::-1]                 # OpenCVはBGR、pygameはRGBなので変換してやる必要がある。
        shape = img_cv.shape[1::-1]               # OpenCVは(高さ, 幅, 色数)、pygameは(幅, 高さ)なのでこれも変換。
#        img_cv = cv2.resize(img_cv, (shape[0]*3, shape[1]*3))
#        pygame_image = pygame.image.frombuffer(img_cv.tostring(), (shape[0]*3, shape[1]*3), 'RGB')   # イメージを用意
        img_cv = cv2.resize(img_cv, (shape[0], shape[1]))
        pygame_image = pygame.image.frombuffer(img_cv.tostring(), (shape[0], shape[1]), 'RGB')   # イメージを用意

        pythonImg_view = pygame.transform.rotate(self.pythonImg, self.e360)
        x, y = self.python_rect.center  # Save its current center.
        self.python_rect = pythonImg_view.get_rect()  # Replace old rect with new rect.
        self.python_rect.center = (x, y)  # Put the new rect's center at old center.

#        screen.blit(pygame_image, (480 - self.point_now_x*3, 270 - self.point_now_y*3))   # 背景を描画
        screen.blit(pygame_image, (480 - self.point_now_x, 270 - self.point_now_y))   # 背景を描画
        screen.blit(pythonImg_view, self.python_rect)     # 蛇を描画


      # 仰瞰視点モード
      elif self.view_mode == DOWN_WARD:
        img_cv = self.robot_view_img
      #if not self.robot_view_img_display.empty() :
        #img_cv = self.robot_view_img_display.get_nowait()
        shape = img_cv.shape
#        img_cv = cv2.resize(img_cv, (960, 540))
        img_cv = img_cv[:,:,::-1]                 # OpenCVはBGR、pygameはRGBなので変換してやる必要がある。
        shape = img_cv.shape[1::-1]               # OpenCVは(高さ, 幅, 色数)、pygameは(幅, 高さ)なのでこれも変換。
        pygame_robot_view_img = pygame.image.frombuffer(img_cv.tostring(), shape, 'RGB')   # イメージを用意

        screen.blit(pygame_robot_view_img, (0, 0))   # 背景を描画


      if self.game_state == WAIT_5_SEC:
        screen.blit(self.wait_5_sec_txt1, (30,50))
        screen.blit(self.wait_5_sec_txt2, (30,120))

      elif self.game_state == HUMAN_JUDGE:
        screen.blit(self.human_judge_txt, (30,50))
        screen.blit(self.turn_txt_o, (480,270))
  """


  def key_handler(self):

    if self.get_key_flag:
      if self.usr_command == ESC:
        # ログの書き込み（上書き注意！！！！）
        print("writing log now...")
        with open("/home/natume-lab/nakamura/SUB_DATA/" + SUB_NAME + "/cmd_log_" + str(self.main_loop_count) + "_" + SUB_NAME + ".txt", mode='w') as f:
          for i in range(len(self.cmd_log)):
            f.write(self.cmd_log[i])
        # マップの書き込み
        print("writing map img...")
        cv2.imwrite("/home/natume-lab/nakamura/SUB_DATA/" + SUB_NAME + "/img_out_comp" + "_" + SUB_NAME + ".jpg", self.img_out_comp)

        pygame.quit()
        sys.exit()

      elif self.usr_command == D:
        if self.game_state == TITLE:
          # ゲーム開始！ (DOWN_WARD)
          print("down ward now...")
          self.view_mode = DOWN_WARD
          self.game_state = CHK_IS
        else:
          print("down ward now...")
          self.view_mode = DOWN_WARD

      elif self.usr_command == Q:
        if self.game_state == TITLE:
          print("quit now...")
          pygame.quit()
          sys.exit()

      elif self.usr_command == W:
        print("writing log now...")
        # ログの書き込み（上書き注意！！！！）
        with open("/home/natume-lab/nakamura/SUB_DATA/" + SUB_NAME + "/cmd_log_" + str(self.main_loop_count) + "_" + SUB_NAME + ".txt", mode='w') as f:
          for i in range(len(self.cmd_log)):
            f.write(self.cmd_log[i])

      elif self.usr_command == M:
        cv2.imwrite("/home/natume-lab/nakamura/SUB_DATA/" + SUB_NAME + "/img_out_comp" + "_" + SUB_NAME+ "_" + str(self.write_map_count) + ".jpg", self.img_out_comp)
        self.write_map_count += 1 # +++++++++++++++++++++++++++++++++++++++++++++++(2019/02/25)
        print("writing map img...")

      elif self.usr_command == I:

        self.find_uxp_flag = True
        self.turn_back_flag = False
        self.could_not_esc_is_flag = False
        self.get_deg_wholemap_flag = False
        self.find_points_back_flag = False

        if self.gpio_status == 1:
          #==============================================

          #         ラズパイに信号を出す。   (交差点ではないところ)

          #==============================================
          self.pub2.publish(0)

          self.gpio_status = 0

        self.game_state = CHK_IS #++++++++++++++++++++++++++++++++
        print("<<Powered to CHK_IS...>>")#++++++++++++++++++++++++++++++++++++++(2019/01/18)


      self.get_key_flag = False

    if self.get_hat_flag1:
      print(self.game_state)
      if self.game_state == HUMAN_JUDGE:
        self.human_dir = ""
        if self.usr_command == Le:
          print("Key_Left DOWN")
          self.human_dir = "L"
        elif self.usr_command == Ri:
          print("Key_RIGHT DOWN")
          self.human_dir = "R"
        elif self.usr_command == St:
          print("Key_STRAIGHT DOWN")
          self.human_dir = "S"
        elif self.usr_command == Ba:
          print("Key_BACK DOWN")
          self.human_dir = "B"
        self.cmd_id += 1

      self.get_hat_flag1 = False
      self.get_hat_flag2 = True


  """
  def load_images(self):

    file_name1 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "abata.png")
    self.pythonImg = pygame.image.load(file_name1).convert_alpha()
    self.python_rect = self.pythonImg.get_rect()
    self.python_rect.center = (480, 270)

    file_name2 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "title.jpg")
    self.titleImg = pygame.image.load(file_name2).convert_alpha()
    self.title_rect = self.titleImg.get_rect()
    self.title_rect.center = (480, 270)
  """

"""
class SpriteSheet:
  #スプライトの一枚絵を管理するクラス
  def __init__(self, filename):
    self.sheet = load_image(filename)
  def image_at(self, rect, colorkey=None):
    #一枚絵からrectで指定した部分を切り取った画像を返す
    rect = Rect(rect)
    image = pygame.Surface(rect.size).convert()
    image.blit(self.sheet, (0, 0), rect)
    return image_colorkey(image, colorkey)
  def images_at(self, rects, colorkey=None):
    #一枚絵からrectsで指定した部分を切り取った画像リストを返す
    images = []
    for rect in rects:
      images.append(self.image_at(rect, colorkey))
    return images



def image_colorkey(image, colorkey):
  #画像にカラーキーを設定
  if colorkey is not None:
    if colorkey is -1:
      colorkey = image.get_at((0,0))
    image.set_colorkey(colorkey, RLEACCEL)
  return image



def load_image(filename, colorkey=None):
  #画像をロード
  filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
  try:
    image = pygame.image.load(filename).convert()
  except pygame.error:
    print ("Cannot load image:" + str(filename))
    raise SystemExit
  return image_colorkey(image, colorkey)
"""

if __name__ == '__main__':
  rospy.init_node('search_unexp_field',anonymous=True)

  # ファイル生成
  SUB_NAME = raw_input("type file name...>>>")
  if SUB_NAME == "miss":
    print("the name is miss.")
    sys.exit()
  try:
    os.makedirs("./" + SUB_NAME)
  except:
    print("the file is exists.")
    sys.exit()

  try:
    suf = SearchUnexpField()
    suf.main()
    rospy.spin()
  except rospy.ROSInterruptException: pass
