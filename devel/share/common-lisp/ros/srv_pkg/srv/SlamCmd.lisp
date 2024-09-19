; Auto-generated. Do not edit!


(cl:in-package srv_pkg-srv)


;//! \htmlinclude SlamCmd-request.msg.html

(cl:defclass <SlamCmd-request> (roslisp-msg-protocol:ros-message)
  ((cmd
    :reader cmd
    :initarg :cmd
    :type cl:fixnum
    :initform 0))
)

(cl:defclass SlamCmd-request (<SlamCmd-request>)
  ())

(cl:defmethod cl:initialize-instance :after ((m <SlamCmd-request>) cl:&rest args)
  (cl:declare (cl:ignorable args))
  (cl:unless (cl:typep m 'SlamCmd-request)
    (roslisp-msg-protocol:msg-deprecation-warning "using old message class name srv_pkg-srv:<SlamCmd-request> is deprecated: use srv_pkg-srv:SlamCmd-request instead.")))

(cl:ensure-generic-function 'cmd-val :lambda-list '(m))
(cl:defmethod cmd-val ((m <SlamCmd-request>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader srv_pkg-srv:cmd-val is deprecated.  Use srv_pkg-srv:cmd instead.")
  (cmd m))
(cl:defmethod roslisp-msg-protocol:serialize ((msg <SlamCmd-request>) ostream)
  "Serializes a message object of type '<SlamCmd-request>"
  (cl:write-byte (cl:ldb (cl:byte 8 0) (cl:slot-value msg 'cmd)) ostream)
)
(cl:defmethod roslisp-msg-protocol:deserialize ((msg <SlamCmd-request>) istream)
  "Deserializes a message object of type '<SlamCmd-request>"
    (cl:setf (cl:ldb (cl:byte 8 0) (cl:slot-value msg 'cmd)) (cl:read-byte istream))
  msg
)
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql '<SlamCmd-request>)))
  "Returns string type for a service object of type '<SlamCmd-request>"
  "srv_pkg/SlamCmdRequest")
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql 'SlamCmd-request)))
  "Returns string type for a service object of type 'SlamCmd-request"
  "srv_pkg/SlamCmdRequest")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql '<SlamCmd-request>)))
  "Returns md5sum for a message object of type '<SlamCmd-request>"
  "12316eeb2759f96b72e22e8fa55290b3")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql 'SlamCmd-request)))
  "Returns md5sum for a message object of type 'SlamCmd-request"
  "12316eeb2759f96b72e22e8fa55290b3")
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql '<SlamCmd-request>)))
  "Returns full string definition for message of type '<SlamCmd-request>"
  (cl:format cl:nil "uint8 cmd~%~%~%"))
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql 'SlamCmd-request)))
  "Returns full string definition for message of type 'SlamCmd-request"
  (cl:format cl:nil "uint8 cmd~%~%~%"))
(cl:defmethod roslisp-msg-protocol:serialization-length ((msg <SlamCmd-request>))
  (cl:+ 0
     1
))
(cl:defmethod roslisp-msg-protocol:ros-message-to-list ((msg <SlamCmd-request>))
  "Converts a ROS message object to a list"
  (cl:list 'SlamCmd-request
    (cl:cons ':cmd (cmd msg))
))
;//! \htmlinclude SlamCmd-response.msg.html

(cl:defclass <SlamCmd-response> (roslisp-msg-protocol:ros-message)
  ((status
    :reader status
    :initarg :status
    :type cl:fixnum
    :initform 0))
)

(cl:defclass SlamCmd-response (<SlamCmd-response>)
  ())

(cl:defmethod cl:initialize-instance :after ((m <SlamCmd-response>) cl:&rest args)
  (cl:declare (cl:ignorable args))
  (cl:unless (cl:typep m 'SlamCmd-response)
    (roslisp-msg-protocol:msg-deprecation-warning "using old message class name srv_pkg-srv:<SlamCmd-response> is deprecated: use srv_pkg-srv:SlamCmd-response instead.")))

(cl:ensure-generic-function 'status-val :lambda-list '(m))
(cl:defmethod status-val ((m <SlamCmd-response>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader srv_pkg-srv:status-val is deprecated.  Use srv_pkg-srv:status instead.")
  (status m))
(cl:defmethod roslisp-msg-protocol:serialize ((msg <SlamCmd-response>) ostream)
  "Serializes a message object of type '<SlamCmd-response>"
  (cl:write-byte (cl:ldb (cl:byte 8 0) (cl:slot-value msg 'status)) ostream)
)
(cl:defmethod roslisp-msg-protocol:deserialize ((msg <SlamCmd-response>) istream)
  "Deserializes a message object of type '<SlamCmd-response>"
    (cl:setf (cl:ldb (cl:byte 8 0) (cl:slot-value msg 'status)) (cl:read-byte istream))
  msg
)
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql '<SlamCmd-response>)))
  "Returns string type for a service object of type '<SlamCmd-response>"
  "srv_pkg/SlamCmdResponse")
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql 'SlamCmd-response)))
  "Returns string type for a service object of type 'SlamCmd-response"
  "srv_pkg/SlamCmdResponse")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql '<SlamCmd-response>)))
  "Returns md5sum for a message object of type '<SlamCmd-response>"
  "12316eeb2759f96b72e22e8fa55290b3")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql 'SlamCmd-response)))
  "Returns md5sum for a message object of type 'SlamCmd-response"
  "12316eeb2759f96b72e22e8fa55290b3")
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql '<SlamCmd-response>)))
  "Returns full string definition for message of type '<SlamCmd-response>"
  (cl:format cl:nil "uint8 status~%~%~%~%"))
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql 'SlamCmd-response)))
  "Returns full string definition for message of type 'SlamCmd-response"
  (cl:format cl:nil "uint8 status~%~%~%~%"))
(cl:defmethod roslisp-msg-protocol:serialization-length ((msg <SlamCmd-response>))
  (cl:+ 0
     1
))
(cl:defmethod roslisp-msg-protocol:ros-message-to-list ((msg <SlamCmd-response>))
  "Converts a ROS message object to a list"
  (cl:list 'SlamCmd-response
    (cl:cons ':status (status msg))
))
(cl:defmethod roslisp-msg-protocol:service-request-type ((msg (cl:eql 'SlamCmd)))
  'SlamCmd-request)
(cl:defmethod roslisp-msg-protocol:service-response-type ((msg (cl:eql 'SlamCmd)))
  'SlamCmd-response)
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql 'SlamCmd)))
  "Returns string type for a service object of type '<SlamCmd>"
  "srv_pkg/SlamCmd")