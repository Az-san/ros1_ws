#!/usr/bin/env python3
# -*- coding: utf-8 -*-




#==================================================

## @file libmap
## @author Kentaro NAKAMURA
## @modified for PyQt5 by Takumi FUJI
## @brief インポート

#==================================================


#==================================================

# Python関係

#==================================================
import rospy
import cv2
import numpy as np
import math
import random
import time
from time import sleep
import pygame
from pygame.locals import *
import os
from datetime import datetime
import pickle
from subprocess import Popen
#from PyQt4 import QtGui, QtCore
from PyQt5 import QtGui, QtCore, QtWidgets

#==================================================

# 自作ライブラリ

#==================================================
#from exp_data import *

#==================================================

# ROS関係

#==================================================
import tf
import actionlib
from cv_bridge import CvBridge, CvBridgeError
from nav_msgs.msg import *
from geometry_msgs.msg import *
from sensor_msgs.msg import LaserScan
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
#from std_msgs.msg import Int16
from std_msgs.msg import Int16, String
from sensor_msgs.msg import Image
from gazebo_msgs.msg import *
from actionlib_msgs.msg import *
import rosnode
from std_srvs.srv import Empty
from srv_pkg.srv import SlamCmd

#==================================================

# パラメータ

#==================================================
GOAL_POINT_METER = [5.3, 0.0, 0.0]
#GOAL_POINT_METER = [3.0, -2.0, 0.0]
GOAL_ITERATION_NUM = 30             # ゴールする回数
TRIAL_ITERATION_NUM = 30            # トライアルの制限回数
