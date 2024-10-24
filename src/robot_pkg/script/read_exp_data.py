#!/usr/bin/env python

import pickle
import sys
sys.path.remove('/opt/ros/kinetic/lib/python2.7/dist-packages')
import cv2
import matplotlib.pyplot as plt
import os
import numpy as np
from scipy import stats
import statistics
from natsort import natsorted

sys.path.append("./import")
from exp_data import *

def readRecordData(file):

    file_list = os.listdir("../data/{}".format(file))
    pkl_list = []
    data_list = []

    for i in range(len(file_list)):
        if ".pkl" in file_list[i]:
            path = "../data/{}/{}".format(file, file_list[i])
            with open(path, 'rb') as web:
                data = pickle.load(web)
            data_list.append(data)
            pkl_list.append(file_list[i])
            #print("{}\t= {}".format(file_list[i], data))

    return pkl_list, data_list


def viewXtablesOnMap(file_name, qtable_data_list, xtable_list):
    file_name_split = file_name.split("_")
    sub_name = file_name_split[0]
    num = file_name_split[1][0]
    maze = "7" if file_name_split[2] == "1" else "8"
    goal = file_name_split[3]
    path = "../doc/"
    map_file_list = os.listdir(path)
    for i in range(len(map_file_list)):
        if sub_name in map_file_list[i]:
            map_pgm = cv2.imread(path + "img_out_comp_{}{}{}{}.jpg".format(sub_name, num, maze, goal))
            map_pgm = cv2.rotate(map_pgm, cv2.ROTATE_90_CLOCKWISE)
            print("img_out_comp_{}{}{}{}.jpg".format(sub_name, num, maze, goal))
            plt.imshow(map_pgm)
            pass

    color = "pink"
    x_table = []
    q_table = []
    for i in range(len(qtable_data_list)):
        if qtable_data_list[i][0] == file_name:
            q_table = qtable_data_list[i][6]
            if qtable_data_list[i][3] == "1":
                x_table = xtable_list[0]
            if qtable_data_list[i][3] == "2":
                x_table = xtable_list[1]
            pass

    resolution = 0.050000
    origin = [-10.000000, -10.000000, 0.000000]
    h, w, _ = map_pgm.shape

    x_x_table_pixel = []
    x_y_table_pixel = []
    for j in range(len(x_table)):
        x_x_table_pixel.append(x_table[j][0]/resolution - origin[0]/resolution)
        x_y_table_pixel.append(h - (x_table[j][1]/resolution - origin[1]/resolution))

    plt.scatter(x_x_table_pixel, x_y_table_pixel, c=color)

    #inc_num = list(range(len(x_table)))
    inc_num = q_table
    for j, txt in enumerate(inc_num):
        plt.annotate(txt, (x_x_table_pixel[j], x_y_table_pixel[j]))
        #plt.annotate("{} : ({:.1f}, {:.1f})".format(j, (x_table[j][0]), (x_table[j][1])), (x_x_table_pixel[j], x_y_table_pixel[j]))

    plt.show()


def calcMeanExpTime(file_date):
    file_num = os.listdir("../data/{}".format(file_date))
    data_list_s = []
    pkl_list_s = []
    num_list = []
    cnt_goal = 0
    time_ave = 0
    time_list = []

    for i in range(len(file_num)):
        file = file_date + "/{}".format(i+1)
        #print(file)
        pkl_list, data_list = readRecordData(file)

        data_list_s.append(data_list)
        pkl_list_s.append(pkl_list)

    for i in range(len(data_list_s)):
        time = 0
        flag = False
        for j in range(len(pkl_list_s[i])):
            if pkl_list_s[i][j] == "Time.pkl":                
                time = data_list_s[i][j]
                #print(time)
            if pkl_list_s[i][j] == "Goal.pkl":
                #print(data_list_s[i][j])
                if data_list_s[i][j] == True:
                    flag = True
                    cnt_goal += 1
                #    print("true")
                #else:
                #    print("false !! 1")
        if flag == True:
            time_ave += time
            time_list.append(time)

    #print(cnt_goal)
    #print(time_ave / cnt_goal)

    return time_list


def calcExpTimeAveStd(file_date_be_list):
    for i in range(len(file_date_be_list)):
        time_list = calcMeanExpTime(file_date_be_list[i])
        #print(len(time_list))
        #for j in range(len(time_list)):
        #    print(time_list[j])
        time_ave = statistics.mean(time_list)
        time_std = statistics.pstdev(time_list)
        print("{}:\tave = {}".format(file_date_be_list[i], time_ave))
        print("{}:\tstd = {}".format(file_date_be_list[i], time_std))


def tTestRel(file_date_be_list):
    time_list_s = []
    for i in range(len(file_date_be_list)):
        time_list = calcMeanExpTime(file_date_be_list[i])
        #print(len(time_list))
        time_list_s.append(time_list)

    for i in range(len(time_list_s)):
        time_list_a = time_list_s[i-1]
        time_list_b = time_list_s[i]

        res = stats.ttest_rel(time_list_a, time_list_b)
        print("{} vs {}:\t{}".format(file_date_be_list[i-1], file_date_be_list[i], res))


def tTestRel_once(file_date_be_a, file_date_be_b):
    time_list_a = calcMeanExpTime(file_date_be_a)
    time_list_b = calcMeanExpTime(file_date_be_b)

    res = stats.ttest_rel(time_list_a, time_list_b)
    print("{} vs {}:\t{}".format(file_date_be_a, file_date_be_b, res))


def rot90cwExpMap():
    for sub_name in os.listdir("../doc/exp_data"):
        for travel_name in os.listdir("../doc/exp_data/{}/nakamura".format(sub_name)):
            path = "../doc/exp_data/{}/nakamura/{}".format(sub_name, travel_name)
            map_jpg = cv2.imread(path + "/img_out_comp_{}.jpg".format(travel_name))
            map_jpg_90_clockwise = cv2.rotate(map_jpg, cv2.ROTATE_90_CLOCKWISE)
            cv2.imwrite(path + "/img_out_comp_{}_rot90.jpg".format(travel_name), map_jpg_90_clockwise)


def createMapYamlFile():
    for sub_name in os.listdir("../doc/exp_data"):
        for travel_name in os.listdir("../doc/exp_data/{}/nakamura".format(sub_name)):
            path = "../doc/exp_data/{}/nakamura/{}/map.yaml".format(sub_name, travel_name)
            s = "\
image: /home/nakken/ros_ws/res_ws/src/robot_pkg/doc/exp_data/{}/nakamura/{}/img_out_comp_{}_rot90.jpg\n\
resolution: 0.050000\n\
origin: [-10.000000, -10.000000, 0.000000]\n\
negate: 0\n\
occupied_thresh: 0.65\n\
free_thresh: 0.196\
            ".format(sub_name, travel_name, travel_name)

            with open(path, mode='w') as f:
                f.write(s)


def calcGoalNum(file_date):
    file_num = os.listdir("../data/{}".format(file_date))
    data_list_s = []
    pkl_list_s = []
    num_list = []
    cnt_goal = 0
    cnt_uxp = 0
    time_list = []

    for i in range(len(file_num)):
        file = file_date + "/{}".format(i+1)
        #print(file)
        pkl_list, data_list = readRecordData(file)

        data_list_s.append(data_list)
        pkl_list_s.append(pkl_list)

    for i in range(len(data_list_s)):
        time = 0
        flag = False
        for j in range(len(pkl_list_s[i])):
            if pkl_list_s[i][j] == "Time.pkl":                
                time = data_list_s[i][j]
            if pkl_list_s[i][j] == "Status.pkl":
                if data_list_s[i][j] == "goal":
                    flag = True
                    cnt_goal += 1
                elif data_list_s[i][j] == "go to unexp":
                    flag = True
                    cnt_uxp += 1

        if flag == True:
            time_list.append(time)

    

    return cnt_goal, cnt_uxp, time_list



def viewQtablesOnMap(file_name, qtable_data_list, xtable_list):
    file_name_split = file_name.split("_")
    sub_name = file_name_split[6]
    num = file_name_split[7][0]
    maze = "7" if file_name_split[8] == "1" else "8"
    goal = file_name_split[9]
    path = "../doc/exp_data"
    path_save_img = ""
    map_file_list = os.listdir(path)
    for i in range(len(map_file_list)):
        if sub_name in map_file_list[i]:
            for data_name in os.listdir("{}/{}/{}".format(path, map_file_list[i], "nakamura")):
                tmp1 = "{}{}{}{}".format(sub_name, num, maze, goal)
                tmp2 = "img_out_comp_{}{}{}{}.jpg".format(sub_name, num, maze, goal)
                if tmp1 in data_name:
                    print("{}/{}/{}/{}/{}".format(path, map_file_list[i], "nakamura", tmp1, tmp2))
                    map_pgm = cv2.imread("{}/{}/{}/{}/{}".format(path, map_file_list[i], "nakamura", tmp1, tmp2))
                    path_save_img = "{}/{}/{}/{}".format(path, map_file_list[i], "nakamura", tmp1)
                    map_pgm = cv2.rotate(map_pgm, cv2.ROTATE_90_CLOCKWISE)
            
            plt.imshow(map_pgm)
            pass

    color = "pink"
    x_table = []
    q_table = []
    for i in range(len(qtable_data_list)):
        if qtable_data_list[i][1] == sub_name \
            and qtable_data_list[i][2] == num \
            and qtable_data_list[i][3] == file_name_split[8] \
            and qtable_data_list[i][4] == goal:
            q_table = qtable_data_list[i][6]
            if qtable_data_list[i][3] == "1":
                x_table = xtable_list[0]
            if qtable_data_list[i][3] == "2":
                x_table = xtable_list[1]
            pass

    resolution = 0.050000
    origin = [-10.000000, -10.000000, 0.000000]
    h, w, _ = map_pgm.shape

    x_x_table_pixel = []
    x_y_table_pixel = []
    for j in range(len(x_table)):
        x_x_table_pixel.append(x_table[j][0]/resolution - origin[0]/resolution)
        x_y_table_pixel.append(h - (x_table[j][1]/resolution - origin[1]/resolution))

    plt.scatter(x_x_table_pixel, x_y_table_pixel, c=color)

    #inc_num = list(range(len(x_table)))
    inc_num = q_table
    for j, txt in enumerate(inc_num):
        plt.annotate(txt, (x_x_table_pixel[j], x_y_table_pixel[j]))
        #plt.annotate("{} : ({:.1f}, {:.1f})".format(j, (x_table[j][0]), (x_table[j][1])), (x_x_table_pixel[j], x_y_table_pixel[j]))

    tmp3 = "img_out_comp_{}{}{}{}_qx.jpg".format(sub_name, num, maze, goal)
    plt.savefig('{}/{}'.format(path_save_img, tmp3))
    plt.close()
    #plt.show()


def calcMapArea(file_name):
    resolution = 0.05

    file_name_split = file_name.split("_")
    sub_name = file_name_split[6]
    num = file_name_split[7][0]
    maze = "7" if file_name_split[8] == "1" else "8"
    goal = file_name_split[9]
    path = "../doc/exp_data"
    path_save_img = ""
    map_file_list = os.listdir(path)
    for i in range(len(map_file_list)):
        if sub_name in map_file_list[i]:
            for data_name in os.listdir("{}/{}/{}".format(path, map_file_list[i], "nakamura")):
                tmp1 = "{}{}{}{}".format(sub_name, num, maze, goal)
                tmp2 = "img_out_comp_{}{}{}{}.jpg".format(sub_name, num, maze, goal)
                if tmp1 in data_name:
                    print("{}/{}/{}/{}/{}".format(path, map_file_list[i], "nakamura", tmp1, tmp2))
                    map_pgm = cv2.imread("{}/{}/{}/{}/{}".format(path, map_file_list[i], "nakamura", tmp1, tmp2))
                    path_save_img = "{}/{}/{}/{}".format(path, map_file_list[i], "nakamura", tmp1)
                    map_pgm = cv2.rotate(map_pgm, cv2.ROTATE_90_CLOCKWISE)

            pass

    cnt = 0
    for i in range(len(map_pgm)):
        for j in range(len(map_pgm[i])):
            if 255 in map_pgm[i][j]:
                cnt += 1
    area = (resolution**2) * cnt

    return area



if __name__ == "__main__":
    #file_date = "2020_12_28_10_46_49_ee"
    #file_date = "2020_12_28_11_0_51_ee"
    #file_date = "2020_12_28_11_6_10_ee"

    #file_date = "2021_1_10_10_41_49_ee"
    #file_date = "2021_1_10_11_3_18_ee"

    #file_date = "2021_1_6_1_10_5_be"
    #file_date = "2021_1_6_19_5_39_be"
    #file_date = "2021_1_6_22_10_35_be"
    #file_date = "2021_1_7_2_15_11_be"

    #file_date = "2021_1_10_17_54_55_ht_1_1_B_be"

    #calcMeanExpTime(file_date)
    #viewXtablesOnMap(file_date)

    #file_date_be_list = ["2021_1_6_1_10_5_be", "2021_1_6_19_5_39_be", "2021_1_6_22_10_35_be", "2021_1_7_2_15_11_be"]

    #file_date_be_list = ["2021_1_11_5_4_30_ht_1_1_B_be", "2021_1_13_3_5_26_ht_2_2_A_be", "2021_1_13_6_57_7_ht_3_1_A_be", "2021_1_13_12_32_24_ht_4_2_A_be", "2021_1_13_17_23_24_ht_5_1_B_be"]
    #file_date_be_list_maze7_goalB = ["2021_1_11_5_4_30_ht_1_1_B_be", "2021_1_13_17_23_24_ht_5_1_B_be"]

    #calcExpTimeAveStd(file_date_be_list)
    #tTestRel(file_date_be_list)
    #tTestRel_once("2021_1_7_2_15_11_be", "2021_1_11_5_4_30_ht_1_1_B_be")
    #tTestRel_once("2021_1_7_2_15_11_be", "2021_1_13_17_23_24_ht_5_1_B_be")



    qtable_data_list = QTABLE_DATA_LIST
    xtable_list = XTABLE_LIST
    #file_name = "ht_5th_1_B_2019_0122"
    #file_name = "sm_5th_1_B_20190227"
    file_name = "yt_5th_1_B_20190128"
    #file_name = "at_5th_1_B_2019_02_26"
    #file_name = "st_5th_1_B_20190206"
    #viewXtablesOnMap(file_name, qtable_data_list, xtable_list)

    #name_list = ["st", "ht", "yt", "at", "sm"]
    name_list = ["ht"]
    

    cnt_goal_list = []
    cnt_uxp_list = []
    time_ave_list = []
    area_list = []
    time_list_list_1 = []
    time_list_list_2 = []
    for name in name_list:
        for data in natsorted(os.listdir("../data")):
            if name in data and os.path.isdir("../data/{}".format(data)):
                file_name_split = data.split("_")
                sub_name = file_name_split[6]
                num = file_name_split[7][0]
                maze = "7" if file_name_split[8] == "1" else "8"
                goal = file_name_split[9]

                if True:
                    #if (num == "2" and maze == "8") or (num == "4" and maze == "8"):
                    #if (num == "1" and maze == "7") or (num == "5" and maze == "7"):
                    #if int(num) < 3:
                    #if int(num) > 3:
                    cnt_goal, cnt_uxp, time_list = calcGoalNum(data)
                    time_ave = statistics.mean(time_list)
                    time_std = statistics.pstdev(time_list)
                    
                    #viewQtablesOnMap(data, qtable_data_list, xtable_list)
                    area = calcMapArea(data)

                    print("{}\t{}\t{}\t{:.2f} + {:.2f}\t{:.2f}".format(name, cnt_goal, cnt_uxp, time_ave, time_std, area))

                    cnt_goal_list.append(cnt_goal)
                    cnt_uxp_list.append(cnt_uxp)
                    time_ave_list.append(time_ave)
                    area_list.append(area)
                    time_list_list_2 += time_list

    print("all sub time ave = {:.2f} + {:.2f}".format(statistics.mean(time_list_list_2), statistics.pstdev(time_list_list_2)))

    # 相関行列を計算
    data_list = [cnt_goal_list, cnt_uxp_list, time_ave_list, area_list]
    data_name_list = ["cnt_goal_list", "cnt_uxp_list", "time_ave_list", "area_list"]
    for i in range(len(data_list)):
        for j in range(len(data_list)):
            if i == j:
                continue
            if i < j:
                continue
            coef = np.corrcoef(data_list[i], data_list[j])
            print(data_name_list[i] + " vs " + data_name_list[j])
            print(coef)
