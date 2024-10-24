#!/usr/bin/env python

import pickle
import sys
#sys.path.remove('/opt/ros/kinetic/lib/python2.7/dist-packages')
#import cv2
import matplotlib.pyplot as plt
import os
import numpy as np
from scipy import stats
import statistics

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


def viewXtablesOnMap(file):
    path = "../data/{}/{}".format(file, "map.pgm")
    map_pgm = cv2.imread(path)
    print(map_pgm)

    plt.imshow(cv2.cvtColor(map_pgm, cv2.COLOR_BGR2RGB))

    color = "pink"
    path = "../data/{}/{}".format(file, "XTable.pkl")
    with open(path, 'rb') as web:
        x_table = pickle.load(web)
    path = "../data/{}/{}".format(file, "QTable.pkl")
    with open(path, 'rb') as web:
        q_table = pickle.load(web)
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
        #plt.annotate(txt, (x_x_table_pixel[j], x_y_table_pixel[j]))
        plt.annotate("{} : ({:.1f}, {:.1f})".format(j, (x_table[j][0]), (x_table[j][1])), (x_x_table_pixel[j], x_y_table_pixel[j]))

    plt.show()


def calcMeanExpTime(file_date):
    file_num = os.listdir("../data/{}".format(file_date))
    data_list_s = []
    pkl_list_s = []
    num_list = []
    cnt_goal = 0
    cnt_status = 0
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
        flag_time = False
        flag_status = False
        for j in range(len(pkl_list_s[i])):
            if pkl_list_s[i][j] == "Time.pkl":                
                time = data_list_s[i][j]
                #print(time)
            if pkl_list_s[i][j] == "Goal.pkl":
                #print(data_list_s[i][j])
                if data_list_s[i][j] == True:
                    flag_time = True
                    cnt_goal += 1
                #    print("true")
                #else:
                #    print("false !! 1")
            if pkl_list_s[i][j] == "Status.pkl":
                print(data_list_s[i][j])
                if data_list_s[i][j] == "goal" or data_list_s[i][j] == "go to unexp":
                    flag_status = True
                    cnt_status += 1
                
        if flag_time == True:
            time_ave += time
            time_list.append(time)

    #print(cnt_goal)
    #print(time_ave / cnt_goal)
    print(cnt_status)


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

    file_date = "2021_1_20_14_37_36_yt_5_1_B_be"

    calcMeanExpTime(file_date)
    #viewXtablesOnMap(file_date)

    #file_date_be_list = ["2021_1_6_1_10_5_be", "2021_1_6_19_5_39_be", "2021_1_6_22_10_35_be", "2021_1_7_2_15_11_be"]

    #file_date_be_list = ["2021_1_11_5_4_30_ht_1_1_B_be", "2021_1_13_3_5_26_ht_2_2_A_be", "2021_1_13_6_57_7_ht_3_1_A_be", "2021_1_13_12_32_24_ht_4_2_A_be", "2021_1_13_17_23_24_ht_5_1_B_be"]
    #file_date_be_list_maze7_goalB = ["2021_1_13_17_23_24_ht_5_1_B_be", "2021_1_14_18_45_19_sm_5_1_B_be"]

    #calcExpTimeAveStd(file_date_be_list_maze7_goalB)
    #tTestRel(file_date_be_list_maze7_goalB)
    #tTestRel_once("2021_1_7_2_15_11_be", "2021_1_13_17_23_24_ht_5_1_B_be")
    #tTestRel_once("2021_1_7_2_15_11_be", "2021_1_14_18_45_19_sm_5_1_B_be")



