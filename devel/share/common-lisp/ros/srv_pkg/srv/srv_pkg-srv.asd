
(cl:in-package :asdf)

(defsystem "srv_pkg-srv"
  :depends-on (:roslisp-msg-protocol :roslisp-utils )
  :components ((:file "_package")
    (:file "SlamCmd" :depends-on ("_package_SlamCmd"))
    (:file "_package_SlamCmd" :depends-on ("_package"))
  ))