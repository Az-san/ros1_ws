#!/usr/bin/env python
# -*- coding: utf-8 -*-




#==================================================

## @file libnav
## @author Kentaro NAKAMURA
## @brief ライブラリクラス

#==================================================




#==================================================

# import

#==================================================
import sys
import roslib

sys.path.append(roslib.packages.get_pkg_dir("robot_pkg") + "/script/import")
from common_import import *

#==================================================

# グローバル

#==================================================




#==================================================

## @class GUI
## @brief GUIのアニメーションを操作する

#==================================================
class GUI(QtGui.QWidget):
    #==================================================
    
    ## @fn __init__
    ## @brief コンストラクタ
    ## @param 
    ## @return

    #==================================================
    def __init__(
        self,
        *args
    ):
        super(QtGui.QWidget, self).__init__()

        #==================================================

        # メンバ変数

        #==================================================
        # FPS
        self.fps = 24

        # imgCallback
        size_img = 1, 1, 3
        self.robot_img = np.zeros(size_img, dtype=np.uint8)

        # guiStateCallback
        self.gui_state = 0

        # GUIに使用する画像の読み込み
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
        # PyQT4の初期化
        self.video_frame = QtGui.QLabel()
        self.lay = QtGui.QVBoxLayout()
        self.lay.setMargin(0)
        self.lay.addWidget(self.video_frame)
        self.setLayout(self.lay)

        # ゲームパットの初期化
        pygame.joystick.init()
        try:
            self.j = pygame.joystick.Joystick(0) # create a joystick instance
            self.j.init() # init instance
            #print 'Joystickの名称: ' + self.j.get_name()
            #print 'ボタン数 : ' + str(self.j.get_numbuttons())
            print 'Joystick Name: ' + self.j.get_name()
            print 'Button number : ' + str(self.j.get_numbuttons())
        except pygame.error:
            #print 'Joystickが見つかりませんでした。'
            print 'No Joystick'

        # pygameの初期化
        pygame.init()


        return




    #==================================================
    
    ## @fn delete
    ## @brief デストラクタ
    ## @param
    ## @return

    #==================================================
    def delete(
        self
    ):
        #==================================================

        # ファイナライズ

        #==================================================


        return


    #==================================================
    
    ## @fn imgCallback
    ## @brief 
    ## @param
    ## @return

    #==================================================
    def imgCallback(
        self,
        data
    ):
        try:
            tmp_sub_img_data = self.bridge.imgmsg_to_cv2(data, "bgr8")
        except CvBridgeError as e:
            print(e)

        #self.robot_view_img = cv2.resize(tmp_sub_img_data, (960, 540))
        self.robot_img = tmp_sub_img_data

        return



    #==================================================
    
    ## @fn guiStateCallback
    ## @brief 
    ## @param
    ## @return

    #==================================================
    def guiStateCallback(
        self,
        data
    ):
        self.gui_state = data.data

        return



    #==================================================
    
    ## @fn 
    ## @brief QT独自スレッドの開始？
    ## @param
    ## @return

    #==================================================
    def start(self):
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.gamepadEvent)
        self.timer.start(1000./self.fps)


    #==================================================
    
    ## @fn 
    ## @brief QTウィンドウ上でのゲームパッドイベント管理（ユーザー定義）
    ## @param
    ## @return

    #==================================================
    def gamepadEvent(self):
        for event in pygame.event.get():
            if event.type == pygame.locals.JOYHATMOTION:
                x, y = self.j.get_hat(0)
                if x == -1:
                    print("Le")
                elif x == 1:
                    print("Ri")
                elif y == 1:
                    print("St")
                elif y == -1:
                    print("Ba")


    #==================================================
    
    ## @fn
    ## @brief QTウィンドウ上でのキーイベント管理（スーパークラス定義）
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
    
    ## @fn 
    ## @brief QTウィンドウ上での描画管理（スーパークラス定義）
    ## @param
    ## @return

    #==================================================
    def paintEvent(self, e):
        frame = self.robot_img

        if self.gui_state == 0:
            # タイトル画面
            img = QtGui.QImage(self.title_img, frame.shape[1], frame.shape[0], QtGui.QImage.Format_RGB888)
        else:
            # ロボットカメラ
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = QtGui.QImage(frame, frame.shape[1], frame.shape[0], QtGui.QImage.Format_RGB888)
        painter = QtGui.QPainter(img)
        # 四角形
        painter.setBrush(QtCore.Qt.yellow)
        if self.gui_state == 2:
            painter.drawRect(102*2, 50*2, 110, 50)
        elif self.gui_state == 3:
            painter.drawRect(102*2, 50*2, 145, 50)
        elif self.gui_state == 4:
            painter.drawRect(102*2, 50*2, 145, 50)
        # 文字
        painter.setBrush(QtCore.Qt.lightGray)
        painter.setPen(QtCore.Qt.red)
        painter.setFont(QtGui.QFont(u'メイリオ', 30, QtGui.QFont.Bold, False))
        if self.gui_state == 2:
            painter.drawText(QtCore.QPoint(105*2, 140), 'WAIT')
        elif self.gui_state == 3:
            painter.drawText(QtCore.QPoint(105*2, 140), 'JUDGE')
        elif self.gui_state == 4:
            painter.drawText(QtCore.QPoint(105*2, 140), 'ERROR')
        # 注視点
        if self.gui_state != 0:
            painter.setPen(QtCore.Qt.cyan)
            painter.drawText(QtCore.QPoint(480*2, 270*2), '+')

        painter.end()

        pix = QtGui.QPixmap.fromImage(img)
        self.video_frame.setPixmap(pix)


    #==================================================
    
    ## @fn 
    ## @brief 描画する画像のロード
    ## @param
    ## @return

    #==================================================
    def shutdown(self):
        self.close() # 閉じる



    #==================================================
    
    ## @fn 
    ## @brief 描画する画像のロード
    ## @param
    ## @return

    #==================================================
    def load_images(self):
        self.title_img = cv2.imread(roslib.packages.get_pkg_dir("robot_pkg") + "/io" + "/titlex2.jpg")



    #==================================================
    
    ## @fn クラスメイン関数
    ## @brief
    ## @param
    ## @return

    #==================================================
    def main(
        self
    ):
        # 描画開始
        self.setWindowFlags(QtCore.Qt.Tool)
        
        self.start()
        self.show()

        return



#==================================================

# メイン

#==================================================
if __name__ == "__main__":
    rospy.init_node(os.path.basename(__file__).split(".")[0])

    try:
        app = QtGui.QApplication(sys.argv)
        gui = GUI(0)
        gui.main()
        rospy.on_shutdown(gui.shutdown) 
        app.exec_()
        rospy.spin()
    except:
        sys.exit(1)
