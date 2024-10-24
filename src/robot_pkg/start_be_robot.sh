#!/bin/sh

source ~/ros1_ws/devel/setup.bash

export TURTLEBOT3_MODEL=waffle

roslaunch robot_pkg robot_and_interface.launch random:=$1 exp_type:="be"
