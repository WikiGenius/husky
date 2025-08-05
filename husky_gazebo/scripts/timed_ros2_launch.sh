#!/bin/bash
#
# Script to delay the launch of a ROS2 launch file
#
# Usage: ./timed_ros2_launch.sh [seconds_delay] [ros2_package] [launch_file] [optional arguments]
#

function showHelp(){
    echo
    echo "Usage: ./timed_ros2_launch.sh [seconds_delay] [ros2_package] [launch_file] [optional arguments]"
    echo
    echo "Example:"
    echo "./timed_ros2_launch.sh 5 gazebo_ros gzserver.launch.py world:=my_world.world"
    echo
}

if [ "$1" = "-h" ] || [ "$#" -lt 3 ]; then
    showHelp
else
    delay=$1
    shift
    echo "[INFO] Waiting for $delay seconds before launching..."
    sleep "$delay"
    echo "[INFO] Launching: ros2 launch $@"
    ros2 launch "$@"
fi
