#!/usr/bin/python3
# coding: UTF-8

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
from time import sleep
from std_msgs.msg import Int16
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError

import hid  # Replacing pygame with hidapi
import sys, os, queue

from map_laser_read1kai_def import *

SCREEN_SIZE = (960, 540)
# Define other constants here (unchanged)

class SearchUnexpField():
    def __init__(self):
        # Initialize ROS, CVBridge, and Subscribers (unchanged)
        # ...

        self.joystick = None
        self.initialize_joystick()

        # ROS Publishers, initialization variables, etc.
        # ...

    def initialize_joystick(self):
        """Initialize joystick with hidapi."""
        try:
            self.joystick = hid.device()
            self.joystick.open(0x046d, 0xc218)  # Replace with the joystick's VID/PID
            self.joystick.set_nonblocking(True)
            print("Joystick connected successfully")
        except IOError:
            print("Joystick not found or connection failed.")

    def commandCallback(self, data):  # ROS subscriber for human command
        self.usr_command = data.data
        # Process the command data as necessary
        # ...

    def gamepadEvent(self):
        if not self.joystick:
            print("No joystick connected.")
            return

        try:
            # Read joystick data
            data = self.joystick.read(64)
            if data:
                hat_x, hat_y = data[0], data[1]  # Adjust indices as per joystick data report structure

                if hat_x == -1:
                    self.pub4.publish(Le)
                    print("Left")
                elif hat_x == 1:
                    self.pub4.publish(Ri)
                    print("Right")
                elif hat_y == 1:
                    self.pub4.publish(St)
                    print("Straight")
                elif hat_y == -1:
                    self.pub4.publish(Ba)
                    print("Back")
        except Exception as e:
            print(f"Joystick read error: {e}")

    def key_handler(self):
        """Handle joystick and keyboard input."""
        if self.get_key_flag:
            # Process key flags, handling specific commands
            # ...

        if self.get_hat_flag1:
            print("Current game state:", self.game_state)
            if self.game_state == HUMAN_JUDGE:
                if self.usr_command == Le:
                    print("Key_Left")
                    self.human_dir = "L"
                elif self.usr_command == Ri:
                    print("Key_Right")
                    self.human_dir = "R"
                elif self.usr_command == St:
                    print("Key_Straight")
                    self.human_dir = "S"
                elif self.usr_command == Ba:
                    print("Key_Back")
                    self.human_dir = "B"
                self.cmd_id += 1
            self.get_hat_flag1 = False
            self.get_hat_flag2 = True

    def main(self):
        # Main application loop and ROS initialization, unchanged
        clock = rospy.Rate(30)  # 30 Hz loop
        while not rospy.is_shutdown():
            # Robot, display, and UI functions (unchanged)
            self.searchUnexp()
            self.key_handler()
            clock.sleep()

if __name__ == '__main__':
    rospy.init_node('search_unexp_field', anonymous=True)

    # Check for directory, initialize SearchUnexpField and main loop (unchanged)
    try:
        suf = SearchUnexpField()
        suf.main()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
