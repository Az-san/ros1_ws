#!/usr/bin/env python3
# -*- coding: utf-8 -*-




#==================================================

## @file libmap
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

## @class LibMap
## @brief マップを使った機能のライブラリ

#==================================================
class LibMap:
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
        self.sub_map_data = OccupancyGrid()
        self.sub_map_resolution = 0.0

        #==================================================

        # ROSインタフェース

        #==================================================
        self.listener = tf.TransformListener()

        self._sub_map = rospy.Subscriber(
            "/map",
            OccupancyGrid,
            self.mapCallback,
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
    
    ## @fn mapCallback
    ## @brief 
    ## @param
    ## @return

    #==================================================
    def mapCallback(
        self,
        data
    ):
        self.sub_map_data = data
        self.sub_map_resolution = data.info.resolution

        return




    #==================================================
    
    ## @fn getMap
    ## @brief mapのresolutionを返す関数
    ## @param
    ## @return

    #==================================================
    def getResolution(
        self
    ):

        return self.sub_map_resolution



    #==================================================
    
    ## @fn getMap
    ## @brief 未探索地域の発見に使うマップ情報
    ## @param
    ## @return

    #==================================================
    def getMap(
        self
    ):
        size_map = self.sub_map_data.info.width, self.sub_map_data.info.height, 1
        tmp_map_out = np.zeros(size_map, dtype=np.int8)

        # マップ情報の初期化
        for y in range(self.sub_map_data.info.height):
            for x in range(self.sub_map_data.info.width):
                i = (self.sub_map_data.info.width - x - 1) + (self.sub_map_data.info.height - y - 1)* self.sub_map_data.info.width
                intensity_map = 1
                if self.sub_map_data.data[i] == 0:
                    intensity_map = 3
                elif self.sub_map_data.data[i] > 0:
                    intensity_map = 2
                tmp_map_out[x][y] = intensity_map
        
        return tmp_map_out



    #==================================================
    
    ## @fn getMap
    ## @brief インターフェイスへの表示に使うマップ情報
    ## @param
    ## @return

    #==================================================
    def getMapImg(
        self
    ):
        size_img = self.sub_map_data.info.width, self.sub_map_data.info.height, 3
        tmp_map_img_out = np.zeros(size_img, dtype=np.uint8)

        # マップ情報の初期化
        for y in range(self.sub_map_data.info.height):
            for x in range(self.sub_map_data.info.width):
                i = (self.sub_map_data.info.width - x - 1) + (self.sub_map_data.info.height - y - 1)* self.sub_map_data.info.width
                intensity_img = (205,205,205)
                if self.sub_map_data.data[i] == 0:
                    intensity_img = (255,255,255)
                elif self.sub_map_data.data[i] > 0:
                    intensity_img = (0,0,0)
                tmp_map_img_out[x][y] = intensity_img
        
        return tmp_map_img_out



    #==================================================
    
    ## @fn getMapOriginPixel
    ## @fn getMapOrigPix 負のインデックス(後ろから数えた場合)を取得
    ## @brief マップ座標上のスタート地点(pixel)
    ## @param
    ## @return

    #==================================================
    def getMapOriginPixel(
        self
    ):
        origin_pixel_x = int(self.sub_map_data.info.height + self.sub_map_data.info.origin.position.x/self.sub_map_data.info.resolution)
        origin_pixel_y = int(self.sub_map_data.info.width + self.sub_map_data.info.origin.position.y/self.sub_map_data.info.resolution)

        return [origin_pixel_x, origin_pixel_y]

    #==================================================
    
    ## @fn getMapOriginMeter
    ## @brief マップ座標上のスタート地点(meter)
    ## @param
    ## @return

    #==================================================
    def getMapOriginMeter(
        self
    ):
        origin_meter_x = self.sub_map_data.info.height * self.sub_map_data.info.resolution + self.sub_map_data.info.origin.position.x
        origin_meter_y = self.sub_map_data.info.width * self.sub_map_data.info.resolution + self.sub_map_data.info.origin.position.y

        return [origin_meter_x, origin_meter_y]



    #==================================================
    
    ## @fn getRobotPointPixel
    ## @brief ロボットのマップ上の現在地点(pixel)
    ## @param
    ## @return

    #==================================================
    def getRobotPointPixel(
        self
    ):
        point = []
        
        try:
            (trans,rot) = self.listener.lookupTransform('/map', '/base_link', rospy.Time(0))
            e = tf.transformations.euler_from_quaternion((rot[0], rot[1], rot[2], rot[3]))

            # convert -pi < theta < pi TO 0 < theta < 360 and 0 < theta < 2pi
            rad = 0
            if e[2] < 0:
                rad = 2*math.pi + e[2]
            else:
                rad = e[2]

            origin_pixel = self.getMapOriginPixel()

            position_pixel_x = int(origin_pixel[0] - trans[1]/self.sub_map_data.info.resolution)
            position_pixel_y = int(origin_pixel[1] - trans[0]/self.sub_map_data.info.resolution)

            point = [position_pixel_x, position_pixel_y, rad]

        except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
            print("robot TF reading ERROR...")
            pass

        return point


    #==================================================
    
    ## @fn getRobotPointMeter
    ## @brief ロボットのマップ上の現在地点(meter)
    ## @param
    ## @return

    #==================================================
    def getRobotPointMeter(
        self
    ):
        point = []
        
        try:
            (trans,rot) = self.listener.lookupTransform('/map', '/base_link', rospy.Time(0))
            e = tf.transformations.euler_from_quaternion((rot[0], rot[1], rot[2], rot[3]))

            # convert -pi < theta < pi TO 0 < theta < 360 and 0 < theta < 2pi
            rad = 0
            if e[2] < 0:
                rad = 2*math.pi + e[2]
            else:
                rad = e[2]

            position_meter_x = trans[0]
            position_meter_y = trans[1]

            point = [position_meter_x, position_meter_y, rad]

        except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
            print("robot TF reading ERROR...")
            pass

        return point



    #==================================================
    
    ## @fn searchUnexpAroundPoint
    ## @brief 自己位置周辺の未探索地域を探す
    ## @param
    ## @return

    #==================================================
    def searchUnexpAroundPointPixel(
        self,
        map_out, 
        inf_points, 
        inf_rad_sorted, 
        sight=10
    ):
        unexp_points = []               # inf_points周辺の未探索地域の座標
        unexp_rad_sorted = []           # inf_rad_sortedからunexpのものを選択
        count_unexp_list = []

        data_height, data_width, _ = map_out.shape

        # 自己位置周辺の未探索地域を探す
        for i in range(len(inf_points)):
            cog_inf_temp = []
            cog_inf = [0,0]
            count_unexp = 0
            # 未探索地域のボーダーピクセルを検索する
            # ボーダーピクセル：地図の探索地域と未探索地域の境界線のこと
            for y in range(inf_points[i][0] - sight + 1, inf_points[i][0] + sight - 1, 1):
                for x in range(inf_points[i][1] - sight + 1, inf_points[i][1] + sight - 1, 1):
                    if y-1 < 0 or data_width < y+1:
                        continue
                    if x-1 < 0 or data_height < x+1:
                        continue
                    if map_out[x][y] == 3 and map_out[x-1][y] != 2 and map_out[x+1][y] != 2 and map_out[x][y-1] != 2 and map_out[x][y+1] != 2:
                        flag = 0
                        if map_out[x-1][y] == 1:
                            flag += 1
                        elif map_out[x+1][y] == 1:
                            flag += 1
                        elif map_out[x][y-1] == 1:
                            flag += 1
                        elif map_out[x][y+1] == 1:
                            flag += 1
                        if flag > 0:
                            count_unexp += 1
                            cog_inf_temp.append([y,x])

            count_unexp_list.append(count_unexp)

            # ボーダーピクセルが20個以上なら、検索エリアを未探索地域とする
            if count_unexp > 25:
                for j in range(count_unexp):
                    for k in range(2):
                        cog_inf[k] += cog_inf_temp[j][k]
                for l in range(2):
                    cog_inf[l] /= count_unexp
                unexp_points.append(cog_inf)
                unexp_rad_sorted.append(inf_rad_sorted[i])

        print("count_unexp_list = {}".format(count_unexp_list))
        print("unexp_rad_sorted = {}".format(unexp_rad_sorted))

        return unexp_points, unexp_rad_sorted



    #==================================================
    
    ## @fn convPixels2Meters
    ## @brief Pixels単位をMeters単位にする
    ## @param
    ## @return

    #==================================================
    def convPixels2Meters(
        self,
        pixels
    ):
        origin_pixel = self.getMapOriginPixel()
        meters = []
        for i in range(len(pixels)):
            x = (origin_pixel[0] - pixels[i][0]) * self.sub_map_resolution
            y = (origin_pixel[1] - pixels[i][1]) * self.sub_map_resolution
            meters.append([x, y])

        return meters



    #==================================================
    
    ## @fn resetTrial
    ## @brief マップを変更する関数
    ## @param
    ## @return

    #==================================================
    def changeMap(
        self,
        map_yaml_path
    ):
        # 注意　ロボットを初期位置に戻すこと！！

        # キルするmap_serverを控える
        nodes = os.popen("rosnode list").readlines()
        kill_node_name_list = []
        for i in range(len(nodes)):
            nodes[i] = nodes[i].replace("\n","")
        for node in nodes:
            if "map_server" in node:
                kill_node_name_list.append(node)

        # 古い地図のmap_serverをキル
        #os.system("rosnode kill /map_server")
        #sleep(5.0)

        # 新しい地図のmap_serverを蘇生
        cmd = 'rosrun map_server map_server {}'.format(map_yaml_path)
        Popen(cmd.split(" "))
        sleep(5.0)
        #sleep(10.0) # move_baseが適応するまで時間がかかった

        # 控えたmap_serverをキル
        for node in kill_node_name_list:
            os.system("rosnode kill " + node)
            sleep(5.0)


        """
        # 新しい地図のmap_serverをキル（組成するとプロセスを占有するため）
        os.system("rosnode kill /map_server")
        sleep(3.0)
        """


        return
