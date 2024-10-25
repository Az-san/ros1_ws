#!/usr/bin/env python3
# -*- coding: utf-8 -*-


#==================================================
## @file libnav
## @original_author Kentaro NAKAMURA
## @modified for python3, PyQt5, hidapi by Takumi FUJI
## @brief ライブラリクラス
#==================================================

#==================================================
# import
#==================================================
import sys
import roslib
import rospy
import cv2
import numpy as np
import hid  # Import hidapi to replace pygame for joystick
from PyQt5 import QtGui, QtCore, QtWidgets
from cv_bridge import CvBridge, CvBridgeError
from std_msgs.msg import Int16, String
from sensor_msgs.msg import Image

sys.path.append(roslib.packages.get_pkg_dir("robot_pkg") + "/script/import")
from common_import import *

#==================================================
# グローバル
#==================================================


#==================================================
## @class GUI
## @brief GUIのアニメーションを操作する
#==================================================
class GUI(QtWidgets.QWidget):
    #==================================================
    ## @fn __init__
    ## @brief コンストラクタ
    ## @param 
    ## @return
    #==================================================
    def __init__(self, *args):
        super(QtWidgets.QWidget, self).__init__()

        #==================================================
        # メンバ変数
        #==================================================
        self.fps = 24
        size_img = 1, 1, 3
        self.robot_img = np.zeros(size_img, dtype=np.uint8)
        self.gui_state = 0
        self.load_images()

        #==================================================
        # ROSインタフェース
        #==================================================
        self.bridge = CvBridge()
        self.sub_img = rospy.Subscriber(
            "/camera/rgb/image_raw", 
            Image, 
            self.imgCallback
        )
        self.sub_gui_state = rospy.Subscriber(
            "/gui_state", 
            Int16, 
            self.guiStateCallback
        )

        #==================================================
        # イニシャライズ
        #==================================================
        # PyQt5 initialization
        self.video_frame = QtWidgets.QLabel()
        self.lay = QtWidgets.QVBoxLayout()
        self.lay.setContentsMargins(0,0,0,0)
        self.lay.addWidget(self.video_frame)
        self.setLayout(self.lay)

        # hidapiでジョイスティックの初期化
        try:
            self.joystick = hid.device()
            self.joystick.open(0x046d, 0xc218)  # Logitech RumblePad 2のVIDとPID
            self.joystick.set_nonblocking(True)
            print("Joystickの名称: Logitech RumblePad 2 USB")
        except IOError:
            print("Joystickが見つかりませんでした。")

        return

    #==================================================
    ## @fn delete
    ## @brief デストラクタ
    ## @param
    ## @return
    #==================================================
    def delete(self):
        return

    #==================================================
    ## @fn imgCallback
    ## @brief 
    ## @param
    ## @return
    #==================================================
    def imgCallback(self, data):
        try:
            tmp_sub_img_data = self.bridge.imgmsg_to_cv2(data, "bgr8")
        except CvBridgeError as e:
            print(e)
        self.robot_img = tmp_sub_img_data
        return

    #==================================================
    ## @fn guiStateCallback
    ## @brief 
    ## @param
    ## @return
    #==================================================
    def guiStateCallback(self, data):
        self.gui_state = data.data
        return

    #==================================================
    ## @fn start
    ## @brief QT独自スレッドの開始
    ## @param
    ## @return
    #==================================================
    def start(self):
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.gamepadEvent)
        self.timer.start(int(1000./self.fps))

    #==================================================
    ## @fn gamepadEvent
    ## @brief QTウィンドウ上でのゲームパッドイベント管理
    ## @param
    ## @return
    #==================================================
    def gamepadEvent(self):
        try:
            data = self.joystick.read(64)
            if data:
                hat_x = data[0]
                hat_y = data[1]

                if hat_x == -1:
                    print("Le")
                elif hat_x == 1:
                    print("Ri")
                elif hat_y == 1:
                    print("St")
                elif hat_y == -1:
                    print("Ba")
        except Exception as e:
            print(f"ジョイスティック入力エラー: {e}")

    #==================================================
    ## @fn keyPressEvent
    ## @brief QTウィンドウ上でのキーイベント管理
    ## @param
    ## @return
    #==================================================
    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()
            sys.exit()
        elif e.key() == QtCore.Qt.Key_D:
            print("D")
        elif e.key() == QtCore.Qt.Key_Q:
            print("Q")
        elif e.key() == QtCore.Qt.Key_R:
            print("R")
        elif e.key() == QtCore.Qt.Key_W:
            print("W")
        elif e.key() == QtCore.Qt.Key_M:
            print("M")
        elif e.key() == QtCore.Qt.Key_I:
            print("I")

    #==================================================
    ## @fn paintEvent
    ## @brief QTウィンドウ上での描画管理
    ## @param
    ## @return
    #==================================================
    def paintEvent(self, e):
        frame = self.robot_img

        if self.gui_state == 0:
            img = QtGui.QImage(self.title_img, frame.shape[1], frame.shape[0], QtGui.QImage.Format_RGB888)
        else:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = QtGui.QImage(frame, frame.shape[1], frame.shape[0], QtGui.QImage.Format_RGB888)
        
        painter = QtGui.QPainter(img)
        painter.setBrush(QtCore.Qt.yellow)
        
        if self.gui_state == 2:
            painter.drawRect(102*2, 50*2, 110, 50)
        elif self.gui_state == 3:
            painter.drawRect(102*2, 50*2, 145, 50)
        elif self.gui_state == 4:
            painter.drawRect(102*2, 50*2, 145, 50)

        painter.setBrush(QtCore.Qt.lightGray)
        painter.setPen(QtCore.Qt.red)
        painter.setFont(QtGui.QFont(u'メイリオ', 30, QtGui.QFont.Bold, False))
        if self.gui_state == 2:
            painter.drawText(QtCore.QPoint(105*2, 140), 'WAIT')
        elif self.gui_state == 3:
            painter.drawText(QtCore.QPoint(105*2, 140), 'JUDGE')
        elif self.gui_state == 4:
            painter.drawText(QtCore.QPoint(105*2, 140), 'ERROR')

        if self.gui_state != 0:
            painter.setPen(QtCore.Qt.cyan)
            painter.drawText(QtCore.QPoint(480*2, 270*2), '+')

        painter.end()

        pix = QtGui.QPixmap.fromImage(img)
        self.video_frame.setPixmap(pix)

    #==================================================
    ## @fn load_images
    ## @brief 描画する画像のロード
    ## @param
    ## @return
    #==================================================
    def load_images(self):
        self.title_img = cv2.imread(roslib.packages.get_pkg_dir("robot_pkg") + "/io" + "/titlex2.jpg")

    #==================================================
    ## @fn shutdown
    ## @brief シャットダウン
    ## @param
    ## @return
    #==================================================
    def shutdown(self):
        self.close()  # 閉じる

    #==================================================
    ## @fn main
    ## @brief クラスメイン関数
    ## @param
    ## @return
    #==================================================
    def main(self):
        self.setWindowFlags(QtCore.Qt.Tool)
        self.start()
        self.show()
        print("Graphic Que")
        return

#==================================================
# メイン
#==================================================
if __name__ == "__main__":
    rospy.init_node(os.path.basename(__file__).split(".")[0])
    app = QtWidgets.QApplication(sys.argv)
    gui = GUI(0)
    gui.main()
    rospy.on_shutdown(gui.shutdown) 
    app.exec_()
    rospy.spin()
