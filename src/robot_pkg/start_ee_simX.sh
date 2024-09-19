#!/bin/sh

#更新したい試行のQ,Xを指定する。（例）bash start_be_sim.sh 2020_10_28_13_40_11_ee

source ~/ros1_ws/devel/setup.bash

export TURTLEBOT3_MODEL=waffle

#コマンドライン引数でマップを選択する（デフォルトはA）

roslaunch robot_pkg simulation_and_navigation_karto.launch type:=ee maze:=${1:-v}
