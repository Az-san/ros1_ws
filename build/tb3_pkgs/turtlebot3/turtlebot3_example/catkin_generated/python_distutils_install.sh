#!/bin/sh

if [ -n "$DESTDIR" ] ; then
    case $DESTDIR in
        /*) # ok
            ;;
        *)
            /bin/echo "DESTDIR argument must be absolute... "
            /bin/echo "otherwise python's distutils will bork things."
            exit 1
    esac
fi

echo_and_run() { echo "+ $@" ; "$@" ; }

echo_and_run cd "/home/user/ros1_ws/src/tb3_pkgs/turtlebot3/turtlebot3_example"

# ensure that Python install destination exists
echo_and_run mkdir -p "$DESTDIR/home/user/ros1_ws/install/lib/python3/dist-packages"

# Note that PYTHONPATH is pulled from the environment to support installing
# into one location when some dependencies were installed in another
# location, #123.
echo_and_run /usr/bin/env \
    PYTHONPATH="/home/user/ros1_ws/install/lib/python3/dist-packages:/home/user/ros1_ws/build/lib/python3/dist-packages:$PYTHONPATH" \
    CATKIN_BINARY_DIR="/home/user/ros1_ws/build" \
    "/usr/bin/python3" \
    "/home/user/ros1_ws/src/tb3_pkgs/turtlebot3/turtlebot3_example/setup.py" \
     \
    build --build-base "/home/user/ros1_ws/build/tb3_pkgs/turtlebot3/turtlebot3_example" \
    install \
    --root="${DESTDIR-/}" \
    --install-layout=deb --prefix="/home/user/ros1_ws/install" --install-scripts="/home/user/ros1_ws/install/bin"