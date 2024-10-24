#!/usr/bin/env python3
# -*- coding: utf-8 -*-




#==================================================

## @file libscan
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

## @class LibScan
## @brief 自作ライブラリクラス

#==================================================
class LibScan:
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
        self.sub_laserscan_data = LaserScan()


        #==================================================

        # ROSインタフェース

        #==================================================
        self.listener = tf.TransformListener()

        self._sub_scan = rospy.Subscriber(
            "/scan",
            LaserScan,
            self.laserCallback,
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
    
    ## @fn laserCallback
    ## @brief 
    ## @param
    ## @return

    #==================================================
    def laserCallback(
        self,
        data
    ):
        self.sub_laserscan_data = data

        return


    #==================================================
    
    ## @fn getLaserInfRad
    ## @brief ロボットが進行可能な方向（rad）を算出する関数
    ## @param
    ## @return

    #==================================================
    def getLaserInfRad(
        self
    ):
        count_rad = 0
        count_inf = 0
        inf_rad_ave = []
        inf_rad = []
        connect = False
        ranges = self.sub_laserscan_data.ranges
        count_inf_5_rads = 0

        for i in range(len(ranges)):
            #if ranges[i] == float("inf"):
            if ranges[i] >= 2.5:         # ハズレ経路からの復帰でバグが出る
                if len(inf_rad) == 0:
                    inf_rad.append([i])
                else:
                    for j in range(len(inf_rad)):
                        if min(inf_rad[j])-5 < i < max(inf_rad[j]) + 5:
                            inf_rad[j].append(i)

                            break

                    else:
                        inf_rad.append([i])

        if len(inf_rad) != 0:
            if 355 < abs(min(inf_rad[0]) - max(inf_rad[-1])) < 360:
                for i in range(len(inf_rad[-1])):
                    inf_rad[-1][i] -= 360
                inf_rad[0].extend(inf_rad[-1])
                inf_rad.pop(-1)

            for i in range(len(inf_rad)):
                if len(inf_rad[i]) > 10:
                    inf_rad_ave.append((sum(inf_rad[i])/len(inf_rad[i])) * self.sub_laserscan_data.angle_increment)

        inf_rad_ave.sort()

        # θ±23°の範囲で複数の分岐点が観測されたら、それらすべてを一つにマージする

        if len(inf_rad_ave) > 1:
            if abs(inf_rad_ave[0]+2*math.pi - inf_rad_ave[-1]) < 0.90:
                c = inf_rad_ave.pop(0)
                d = inf_rad_ave.pop(-1)
                inf_rad_ave.insert(i,((c+2*math.pi+d)/2)%(2*math.pi))

            for i in range(1,len(inf_rad_ave)):
                if len(inf_rad_ave) <= i:

                    break

                elif len(inf_rad_ave) > 1:
                    if abs(inf_rad_ave[i] - inf_rad_ave[i-1]) < 0.90:
                        c = inf_rad_ave.pop(i)
                        d = inf_rad_ave.pop(i-1)
                        inf_rad_ave.insert(i,(c+d)/2)

        rad = 0
        
        try:
            (trans,rot) = self.listener.lookupTransform('/map', '/base_link', rospy.Time(0))
            e = tf.transformations.euler_from_quaternion((rot[0], rot[1], rot[2], rot[3]))

            # convert -pi < theta < pi TO 0 < theta < 360 and 0 < theta < 2pi
            rad = 0
            if e[2] < 0:
                rad = 2*math.pi + e[2]
            else:
                rad = e[2]

        except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
            print("robot TF reading ERROR...")
            pass

        inf_rad_ave_sorted = []

        for i in range(len(inf_rad_ave)):
            inf_rad_ave_sorted.append((inf_rad_ave[i] + rad)%(2*math.pi))
        inf_rad_ave_sorted.sort()

        return inf_rad_ave_sorted




    #==================================================
    
    ## @fn getAheadDistance
    ## @brief ロボット前方の障害物との距離（ｍ）を算出する関数
    ## @param
    ## @return

    #==================================================
    def getAheadDistance(
        self
    ):

        return (self.sub_laserscan_data.ranges[0] + self.sub_laserscan_data.ranges[-1])/2



    #==================================================
    
    ## @fn getLaserInfPointPixel
    ## @brief 
    ## @param
    ## @return

    #==================================================
    def getLaserInfPointPixel(
        self,
        inf_rad_sorted,
        position_pixel_x,
        position_pixel_y,
        resolution,
        distance = 2.2
    ):
        inf_points = []

        for j in range(len(inf_rad_sorted)):
            inf_points.append([
                int(position_pixel_x - distance * math.sin(inf_rad_sorted[j])/resolution), \
                int(position_pixel_y - distance * math.cos(inf_rad_sorted[j])/resolution), \
                inf_rad_sorted[j]
            ])
        
        return inf_points

    #==================================================
    
    ## @fn getLaserInfPointMeter
    ## @brief 
    ## @param
    ## @return

    #==================================================
    def getLaserInfPointMeter(
        self,
        inf_rad_sorted,
        position_meter,
        distance = 2.2
    ):
        inf_points = []

        for j in range(len(inf_rad_sorted)):
            inf_points.append([
                position_meter[0] + distance * math.cos(inf_rad_sorted[j]), \
                position_meter[1] + distance * math.sin(inf_rad_sorted[j]), \
                inf_rad_sorted[j]
            ])
        
        return inf_points
