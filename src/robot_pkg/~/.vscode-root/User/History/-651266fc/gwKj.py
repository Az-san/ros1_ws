#!/usr/bin/python
# coding: UTF-8

#####################################################
#                                                   #
#   <@author>                                       #
#                                                   #
#   Kentaro Nakamura                                #
#   mail：p238046k@mail.kyutech.jp                   #
#                                                   #
#####################################################

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
import hid  # Replace pygame with hidapi for joystick support

def getLaserInfDeg(data):  # LRFが無限遠に行った方向（角度）を計測する
    count_deg = 0
    count_inf = 0
    inf_rad = []
    inf_deg = []
    connect = False
    ranges = data.ranges
    count_inf_5_degs = 0

    for i in range(len(ranges)):
        if ranges[i] >= 2.5:  # ハズレ経路からの復帰でバグが出る
            if len(inf_deg) == 0:
                inf_deg.append([i])
            else:
                for j in range(len(inf_deg)):
                    if min(inf_deg[j]) - 5 < i < max(inf_deg[j]) + 5:
                        inf_deg[j].append(i)
                        break
                else:
                    inf_deg.append([i])

    if len(inf_deg) != 0:
        if 355 < abs(min(inf_deg[0]) - max(inf_deg[-1])) < 360:
            for i in range(len(inf_deg[-1])):
                inf_deg[-1][i] -= 360
            inf_deg[0].extend(inf_deg[-1])
            inf_deg.pop(-1)

        for i in range(len(inf_deg)):
            if len(inf_deg[i]) > 10:
                inf_rad.append((sum(inf_deg[i]) / len(inf_deg[i])) * data.angle_increment)

    inf_rad.sort()

    if len(inf_rad) > 1:
        if abs(inf_rad[0] + 2 * math.pi - inf_rad[-1]) < 0.90:
            c = inf_rad.pop(0)
            d = inf_rad.pop(-1)
            inf_rad.insert(i, ((c + 2 * math.pi + d) / 2) % (2 * math.pi))

        for i in range(1, len(inf_rad)):
            if len(inf_rad) <= i:
                break
            elif len(inf_rad) > 1:
                if abs(inf_rad[i] - inf_rad[i - 1]) < 0.90:
                    c = inf_rad.pop(i)
                    d = inf_rad.pop(i - 1)
                    inf_rad.insert(i, (c + d) / 2)

    return inf_rad

def searchUnexpAroundPoint(map_out, inf_points, inf_deg_sorted, sight):
    unexp_points = []  # inf_points周辺の未探索地域の座標
    unexp_deg_sorted = []  # inf_deg_sortedからunexpのものを選択
    data_height, data_width, _ = map_out.shape

    # 自己位置周辺の未探索地域を探す
    for i in range(len(inf_points)):
        cog_inf_temp = []
        cog_inf = [0, 0]
        count_unexp = 0
        for y in range(inf_points[i][0] - sight + 1, inf_points[i][0] + sight - 1, 1):
            for x in range(inf_points[i][1] - sight + 1, inf_points[i][1] + sight - 1, 1):
                if y - 1 < 0 or data_width < y + 1:
                    continue
                if x - 1 < 0 or data_height < x + 1:
                    continue
                if map_out[x][y] == 3 and map_out[x - 1][y] != 2 and map_out[x + 1][y] != 2 and map_out[x][y - 1] != 2 and map_out[x][y + 1] != 2:
                    flag = 0
                    if map_out[x - 1][y] == 1:
                        flag += 1
                    elif map_out[x + 1][y] == 1:
                        flag += 1
                    elif map_out[x][y - 1] == 1:
                        flag += 1
                    elif map_out[x][y + 1] == 1:
                        flag += 1
                    if flag > 0:
                        count_unexp += 1
                        cog_inf_temp.append([y, x])

        if count_unexp > 25:
            for j in range(count_unexp):
                for k in range(2):
                    cog_inf[k] += cog_inf_temp[j][k]
            for l in range(2):
                cog_inf[l] /= count_unexp
            unexp_points.append(cog_inf)
            unexp_deg_sorted.append(inf_deg_sorted[i])

    return unexp_points, unexp_deg_sorted

def gamePadCmd():
    try:
        j = hid.device()
        j.open(0x046d, 0xc218)  # Logitech RumblePad 2のVIDとPID
        j.set_nonblocking(True)
        print("Joystick initialized: Logitech RumblePad 2")
    except IOError:
        print("Joystick not found.")
        return None

    while not rospy.is_shutdown():
        data = j.read(64)
        if data:
            hat_x = data[0]
            hat_y = data[1]

            if hat_x == -1:
                print("Key_Left DOWN")
                return "L"
            elif hat_x == 1:
                print("Key_RIGHT DOWN")
                return "R"
            elif hat_y == 1:
                print("Key_STRAIGHT DOWN")
                return "S"
            elif hat_y == -1:
                print("Key_BACK DOWN")
                return "B"

def drawSearchingUnexp(img_out, point_now_x, point_now_y, inf_points, unexp_points):
    # 現在地点にドットを打つ
    cv2.circle(img_out, (point_now_x, point_now_y), 5, (200, 0, 0), thickness=-1)

    # LRFが無限遠に行った方向にドットを打つ
    if len(inf_points) != 0:
        for i in range(len(inf_points)):
            cv2.circle(img_out, (inf_points[i][0], inf_points[i][1]), 5, (200, 0, 0), thickness=-1)

    # unexp_pointsとsightの描画
    if len(unexp_points) != 0:
        for i in range(len(unexp_points)):
            cv2.circle(img_out, (int(unexp_points[i][0]), int(unexp_points[i][1])), 5, (0, 0, 200), thickness=-1)

    return img_out

def searchUnexpWholeMap(map_out):
    border_points = []
    count_unexp = 0
    data_height, data_width, _ = map_out.shape
    cog_inf_temp = []
    cog_inf = [0, 0]
    count_unexp = 0
    for x in range(data_height):
        for y in range(data_width):
            if y - 1 < 0 or data_width < y + 1:
                continue
            if x - 1 < 0 or data_height < x + 1:
                continue
            if map_out[x][y] == 3 and map_out[x - 1][y] != 2 and map_out[x + 1][y] != 2 and map_out[x][y - 1] != 2 and map_out[x][y + 1] != 2:
                flag = 0
                if map_out[x - 1][y] == 1:
                    flag += 1
                elif map_out[x + 1][y] == 1:
                    flag += 1
                elif map_out[x][y - 1] == 1:
                    flag += 1
                elif map_out[x][y + 1] == 1:
                    flag += 1
                if flag > 0:
                    count_unexp += 1
                    border_points.append([y, x])

    border_points_cog = []
    for i in range(len(border_class)):
        count = 0
        temp_x = 0
        temp_y = 0
        if len(border_class[i]) < 40:
            continue
        for j in range(len(border_class[i])):
            temp_x += border_class[i][j][0]
            temp_y += border_class[i][j][1]
            count += 1
        border_points_cog.append([int(temp_x / count), int(temp_y / count)])

    return border_points_cog
