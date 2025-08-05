#!/usr/bin/env python3
"""
Shortcut: load the Clearpath play-pen world **with the same camera args**.

Usage:
  ros2 launch husky_gazebo playpen_with_realsense.launch.py help:=true
  ros2 launch husky_gazebo playpen_with_realsense.launch.py realsense_enabled:=true world_name:=<path to world>:
  <path to world> currently:
  /home/elyamani/Main/programming/ros2_ws/husky_ws/install/husky_gazebo/share/husky_gazebo/worlds/terrain_1.world | clearpath_playpen.world
"""
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    OpaqueFunction,
    Shutdown,
)
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare

# Function to print usage and exit

def show_usage(context, *args, **kwargs):
    print(__doc__)
    return [Shutdown()]

# Top-level launch arguments, including help
TOP_ARGS = [
    DeclareLaunchArgument(
        'help', default_value='false', choices=['true', 'false'],
        description='Display this help message and exit'
    ),
    DeclareLaunchArgument('realsense_enabled', default_value='false'),
    DeclareLaunchArgument('realsense_mount', default_value='sensor_arch_mount_link'),
    DeclareLaunchArgument('realsense_xyz', default_value='0.02 0 0.025'),
    DeclareLaunchArgument('realsense_rpy', default_value='0 0 0'),
    DeclareLaunchArgument(
        'world_name',
        default_value=PathJoinSubstitution([
            FindPackageShare('husky_gazebo'), 'worlds', 'terrain_1.world'
        ]),
        description='Path to Gazebo world file (relative to GAZEBO_RESOURCE_PATH)'
    ),
]


def generate_launch_description():
    # If help flag is set, show usage and shutdown immediately
    help_action = OpaqueFunction(
        function=show_usage,
        condition=IfCondition(LaunchConfiguration('help'))
    )

    # Include the main Gazebo launch only when help is false
    gazebo_launch = PathJoinSubstitution([
        FindPackageShare('husky_gazebo'), 'launch', 'gazebo_with_realsense.launch.py'
    ])

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(gazebo_launch),
        condition=UnlessCondition(LaunchConfiguration('help')),
        launch_arguments=[
            ('world_path', LaunchConfiguration('world_name')),
            ('realsense_enabled', LaunchConfiguration('realsense_enabled')),
            ('realsense_mount', LaunchConfiguration('realsense_mount')),
            ('realsense_xyz', LaunchConfiguration('realsense_xyz')),
            ('realsense_rpy', LaunchConfiguration('realsense_rpy')),
        ],
    )

    return LaunchDescription(TOP_ARGS + [help_action, gazebo])
