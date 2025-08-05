#!/bin/bash

if [ "$1" = "-h" ] || [ "$#" -lt 3 ]; then
    echo "Usage: ./timed_ros2_run.sh [delay] [package] [executable] [optional arguments]"
else
    delay=$1
    shift
    echo "[INFO] Waiting for $delay seconds..."
    sleep "$delay"
    echo "[INFO] Running: ros2 run $@"
    ros2 run "$@"
fi
