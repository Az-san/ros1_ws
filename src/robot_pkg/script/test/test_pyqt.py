#! /usr/bin/python3
# -*- coding: utf-8 -*-

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

import hid  # Using hidapi for joystick handling
import sys, os

import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

from PyQt5 import QtGui, QtCore, QtWidgets  # Updated for PyQt5 compatibility

# Action codes
ESC, D, Q, R, W, M, I, Le, Ri, St, Ba = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

class QtCapture(QtWidgets.QWidget):
    def __init__(self, *args):
        super(QtWidgets.QWidget, self).__init__()

        self.fps = 24
        self.video_frame = QtWidgets.QLabel()
        self.lay = QtWidgets.QVBoxLayout()
        self.lay.setContentsMargins(0, 0, 0, 0)
        self.lay.addWidget(self.video_frame)
        self.setLayout(self.lay)

        self.bridge = CvBridge()
        self.sub3 = rospy.Subscriber("/camera/rgb/image_raw", Image, self.imageCallback)
        self.sub4 = rospy.Subscriber("/robot_state", Int16, self.stateCallback)

        self.pub4 = rospy.Publisher('human_command', Int16, queue_size=1)

        size_img = 1, 1, 3
        self.robot_view_img = np.zeros(size_img, dtype=np.uint8)
        self.robot_state = 0

        # Initialize joystick with hidapi
        try:
            self.joystick = hid.device()
            self.joystick.open(0x046d, 0xc218)  # Example VID and PID for Logitech; change if needed
            self.joystick.set_nonblocking(True)
            print('Joystick connected: Logitech RumblePad 2 USB')
        except IOError:
            print('Joystick not found.')

        # Load images
        self.load_images()

        # PyQt window settings
        self.setWindowFlags(QtCore.Qt.Tool)
        self.start()
        self.show()

    def imageCallback(self, data):  # Update video feed
        try:
            robot_view_img_temp = self.bridge.imgmsg_to_cv2(data, "bgr8")
            self.robot_view_img = robot_view_img_temp
        except CvBridgeError as e:
            print(e)

    def stateCallback(self, data):  # Update robot state
        self.robot_state = data.data

    def start(self):
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.gamepadEvent)
        self.timer.start(int(1000. / self.fps))

    def gamepadEvent(self):
        # Reading joystick events with hidapi
        try:
            data = self.joystick.read(64)
            if data:
                hat_x, hat_y = data[0], data[1]  # Check hat_x and hat_y based on actual report structure
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
            print(f"Error reading joystick input: {e}")

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.pub4.publish(ESC)
            self.close()
            sys.exit()
        elif e.key() == QtCore.Qt.Key_D:
            self.pub4.publish(D)
            print("D")
        elif e.key() == QtCore.Qt.Key_Q:
            self.pub4.publish(Q)
            print("Q")
        elif e.key() == QtCore.Qt.Key_R:
            self.pub4.publish(R)
            print("R")
        elif e.key() == QtCore.Qt.Key_W:
            self.pub4.publish(W)
            print("W")
        elif e.key() == QtCore.Qt.Key_M:
            self.pub4.publish(M)
            print("M")
        elif e.key() == QtCore.Qt.Key_I:
            self.pub4.publish(I)
            print("I")

    def paintEvent(self, e):
        frame = self.robot_view_img

        if self.robot_state == 0:
            img = QtGui.QImage(self.titleImg, frame.shape[1], frame.shape[0], QtGui.QImage.Format_RGB888)
        else:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = QtGui.QImage(frame, frame.shape[1], frame.shape[0], QtGui.QImage.Format_RGB888)
        painter = QtGui.QPainter(img)
        painter.setBrush(QtCore.Qt.yellow)
        if self.robot_state == 2:
            painter.drawRect(102*2, 50*2, 110, 50)
        elif self.robot_state == 3:
            painter.drawRect(102*2, 50*2, 145, 50)
        elif self.robot_state == 4:
            painter.drawRect(102*2, 50*2, 145, 50)

        painter.setBrush(QtCore.Qt.lightGray)
        painter.setPen(QtCore.Qt.red)
        painter.setFont(QtGui.QFont('Arial', 30, QtGui.QFont.Bold, False))
        if self.robot_state == 2:
            painter.drawText(QtCore.QPoint(105*2, 140), 'WAIT')
        elif self.robot_state == 3:
            painter.drawText(QtCore.QPoint(105*2, 140), 'JUDGE')
        elif self.robot_state == 4:
            painter.drawText(QtCore.QPoint(105*2, 140), 'ERROR')
        if self.robot_state != 0:
            painter.setPen(QtCore.Qt.cyan)
            painter.drawText(QtCore.QPoint(480*2, 270*2), '+')

        painter.end()
        pix = QtGui.QPixmap.fromImage(img)
        self.video_frame.setPixmap(pix)

    def shutdown(self):
        print("Shutting down...")
        self.close()

    def load_images(self):
        file_name2 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "titlex2.jpg")
        self.titleImg = cv2.imread(file_name2)


if __name__ == '__main__':
    rospy.init_node('robot_img_view', anonymous=True)

    try:
        app = QtWidgets.QApplication(sys.argv)
        capture = QtCapture(0)
        rospy.on_shutdown(capture.shutdown)
        app.exec_()
        rospy.spin()

    except rospy.ROSInterruptException:
        pass
