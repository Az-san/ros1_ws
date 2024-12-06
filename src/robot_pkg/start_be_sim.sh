#!/bin/sh

#実験するQ,Xファイルを指定する。（例）bash start_be_sim.sh 2020_12_14_20_8_57_ee

source ~/ros1_ws/devel/setup.bash

export TURTLEBOT3_MODEL=waffle

roslaunch robot_pkg simulation_and_navigation.launch maze:=$1 data_file:=$2 # マップが無いところでロボットの挙動がおかしくなる

#roslaunch robot_pkg simulation_and_navigation_gmapping.launch maze:=$1 data_file:=$2 type:=be
