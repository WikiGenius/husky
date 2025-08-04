#!/usr/bin/env python3
"""
Shortcut: load the Clearpath play-pen world **with the same camera args**.
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare

# Simply expose the same arguments so CLI can set them once.
TOP_ARGS = [
    DeclareLaunchArgument('realsense_enabled', default_value='false'),
    DeclareLaunchArgument('realsense_mount',   default_value='sensor_arch_mount_link'),
    DeclareLaunchArgument('realsense_xyz',     default_value='0.02 0 0.025'),
    DeclareLaunchArgument('realsense_rpy',     default_value='0 0 0'),
]

def generate_launch_description():

    world_path = PathJoinSubstitution(
        [FindPackageShare('husky_gazebo'), 'worlds', 'clearpath_playpen.world'])

    gazebo_launch = PathJoinSubstitution(
        [FindPackageShare('husky_gazebo'), 'launch',
         'gazebo_with_realsense.launch.py'])

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(gazebo_launch),
        launch_arguments={
            'world_path':        world_path,
            'realsense_enabled': LaunchConfiguration('realsense_enabled'),
            'realsense_mount':   LaunchConfiguration('realsense_mount'),
            'realsense_xyz':     LaunchConfiguration('realsense_xyz'),
            'realsense_rpy':     LaunchConfiguration('realsense_rpy'),
        }.items())

    return LaunchDescription(TOP_ARGS + [gazebo])
