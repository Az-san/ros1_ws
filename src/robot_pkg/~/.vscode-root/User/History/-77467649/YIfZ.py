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

import hid  # Replacing pygame with hidapi for joystick handling
import sys, os, queue

from map_laser_read1kai_def import *

SCREEN_SIZE = (960, 540)
# Define other constants here as needed

class SearchUnexpField():
    def __init__(self):
        # ROS Initialization, CVBridge, and Subscribers
        self.bridge = CvBridge()
        self.subscriber = rospy.Subscriber("/camera/rgb/image_raw", Image, self.imageCallback)
        self.pub4 = rospy.Publisher('human_command', Int16, queue_size=1)

        self.joystick = None
        self.initialize_joystick()  # Initialize joystick with hidapi

        # Other ROS Publishers, initialization variables, etc.

    def initialize_joystick(self):
        """Initialize joystick with hidapi."""
        try:
            self.joystick = hid.device()
            self.joystick.open(0x046d, 0xc218)  # Replace with your joystick's VID and PID
            self.joystick.set_nonblocking(True)
            print("Joystick connected successfully.")
        except IOError:
            print("Joystick not found or connection failed.")

    def commandCallback(self, data):  # ROS subscriber for human command
        self.usr_command = data.data
        # Process command data as necessary

    def gamepadEvent(self):
        """Handle joystick events and publish commands."""
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
            # Process key flags for specific commands
            pass  # Add specific key handling code here if needed

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
        # Main application loop and ROS initialization
        clock = rospy.Rate(30)  # 30 Hz loop
        while not rospy.is_shutdown():
            # Process robot, display, and UI functions
            self.searchUnexp()
            self.key_handler()
            clock.sleep()

if __name__ == '__main__':
    rospy.init_node('search_unexp_field', anonymous=True)

    # Directory check, initialization, and main loop
    try:
        suf = SearchUnexpField()
        suf.main()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
