#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pickle
import csv
import numpy as np

def read_pkl(path):
    with open(path + "/Time.pkl", "rb") as web:
        time = pickle.load(web)
    with open(path + "/x_id.pkl", "rb") as web:
        x_id = pickle.load(web)
    with open(path + "/XTable.pkl", "rb") as web:
        xtable = pickle.load(web)
    with open(path + "/fork_num.pkl", "rb") as web:
        fork_num = pickle.load(web)
    with open(path + "/HumanDecidedDirection.pkl", "rb") as web:
        h_decideddirection = pickle.load(web)
    with open(path + "/RobotDecidedDirection.pkl", "rb") as web:
        r_decideddirection = pickle.load(web)
    with open(path + "/DecidedDirection.pkl", "rb") as web:
        decideddirection = pickle.load(web)
    with open(path + "/ErrP.pkl", "rb") as web:
        errp = pickle.load(web)
    data = {"tim":time,"xid":x_id,"xta":xtable,"fok":fork_num,"hde":h_decideddirection,"rde":r_decideddirection,"dec":decideddirection,"err":errp}

    return data

def convertX(data):
    x_id = data["xid"]
    xtable = data["xta"]
    conX = []
    for i in range(len(x_id)):
        conX.append(xtable[x_id[i]])
    return conX

if __name__ == '__main__':
    path = input("Input folder name: ")
    path = "/home/user/ros1_ws/src/robot_pkg/data/" + path
    data = read_pkl(path)
    print(f"data length = {len(data['tim'])}")
    conX = convertX(data)
    label = ["Time", "X_id", "X_position", "Fork_num","HumanDecidedDirection", "RobotDecidedDirection", "DecidedDirection", "ErrP"]
    data2d = [data["tim"], data["xid"], conX, data["fok"], data["hde"], data["rde"], data["dec"], data["err"]]
    data2d_t = np.array(data2d).T.tolist()
    data2d_t.insert(0,label)
    with open(path + "/logs.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerows(data2d_t)
        print(f"csv log saved in {path}")

