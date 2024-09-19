;; Auto-generated. Do not edit!


(when (boundp 'srv_pkg::SlamCmd)
  (if (not (find-package "SRV_PKG"))
    (make-package "SRV_PKG"))
  (shadow 'SlamCmd (find-package "SRV_PKG")))
(unless (find-package "SRV_PKG::SLAMCMD")
  (make-package "SRV_PKG::SLAMCMD"))
(unless (find-package "SRV_PKG::SLAMCMDREQUEST")
  (make-package "SRV_PKG::SLAMCMDREQUEST"))
(unless (find-package "SRV_PKG::SLAMCMDRESPONSE")
  (make-package "SRV_PKG::SLAMCMDRESPONSE"))

(in-package "ROS")





(defclass srv_pkg::SlamCmdRequest
  :super ros::object
  :slots (_cmd ))

(defmethod srv_pkg::SlamCmdRequest
  (:init
   (&key
    ((:cmd __cmd) 0)
    )
   (send-super :init)
   (setq _cmd (round __cmd))
   self)
  (:cmd
   (&optional __cmd)
   (if __cmd (setq _cmd __cmd)) _cmd)
  (:serialization-length
   ()
   (+
    ;; uint8 _cmd
    1
    ))
  (:serialize
   (&optional strm)
   (let ((s (if strm strm
              (make-string-output-stream (send self :serialization-length)))))
     ;; uint8 _cmd
       (write-byte _cmd s)
     ;;
     (if (null strm) (get-output-stream-string s))))
  (:deserialize
   (buf &optional (ptr- 0))
   ;; uint8 _cmd
     (setq _cmd (sys::peek buf ptr- :char)) (incf ptr- 1)
   ;;
   self)
  )

(defclass srv_pkg::SlamCmdResponse
  :super ros::object
  :slots (_status ))

(defmethod srv_pkg::SlamCmdResponse
  (:init
   (&key
    ((:status __status) 0)
    )
   (send-super :init)
   (setq _status (round __status))
   self)
  (:status
   (&optional __status)
   (if __status (setq _status __status)) _status)
  (:serialization-length
   ()
   (+
    ;; uint8 _status
    1
    ))
  (:serialize
   (&optional strm)
   (let ((s (if strm strm
              (make-string-output-stream (send self :serialization-length)))))
     ;; uint8 _status
       (write-byte _status s)
     ;;
     (if (null strm) (get-output-stream-string s))))
  (:deserialize
   (buf &optional (ptr- 0))
   ;; uint8 _status
     (setq _status (sys::peek buf ptr- :char)) (incf ptr- 1)
   ;;
   self)
  )

(defclass srv_pkg::SlamCmd
  :super ros::object
  :slots ())

(setf (get srv_pkg::SlamCmd :md5sum-) "12316eeb2759f96b72e22e8fa55290b3")
(setf (get srv_pkg::SlamCmd :datatype-) "srv_pkg/SlamCmd")
(setf (get srv_pkg::SlamCmd :request) srv_pkg::SlamCmdRequest)
(setf (get srv_pkg::SlamCmd :response) srv_pkg::SlamCmdResponse)

(defmethod srv_pkg::SlamCmdRequest
  (:response () (instance srv_pkg::SlamCmdResponse :init)))

(setf (get srv_pkg::SlamCmdRequest :md5sum-) "12316eeb2759f96b72e22e8fa55290b3")
(setf (get srv_pkg::SlamCmdRequest :datatype-) "srv_pkg/SlamCmdRequest")
(setf (get srv_pkg::SlamCmdRequest :definition-)
      "uint8 cmd
---
uint8 status

")

(setf (get srv_pkg::SlamCmdResponse :md5sum-) "12316eeb2759f96b72e22e8fa55290b3")
(setf (get srv_pkg::SlamCmdResponse :datatype-) "srv_pkg/SlamCmdResponse")
(setf (get srv_pkg::SlamCmdResponse :definition-)
      "uint8 cmd
---
uint8 status

")



(provide :srv_pkg/SlamCmd "12316eeb2759f96b72e22e8fa55290b3")


