#!/usr/bin/env python3
"""
Gazebo + Husky *with* optional Intel® RealSense camera.

This file is a **non-destructive overlay** for the default gazebo.launch.py:
  • Adds launch-time flags to enable/pose the camera.
  • Sets GAZEBO_MODEL_PATH / GAZEBO_PLUGIN_PATH so
    librealsense_gazebo_plugin.so and meshes are discoverable.
  • Leaves controllers / tele-op exactly as upstream.

Usage (top-plate mount, Z = 0.50 m):
    ros2 launch husky_gazebo gazebo_with_realsense.launch.py \
         world_path:=/path/to/world.sdf \
         realsense_enabled:=true \
         realsense_mount:=top_plate_link \
         realsense_xyz:="0 0 0.50" \
         realsense_rpy:="0 0 0"
"""
from pathlib import Path

from launch import LaunchDescription
from launch.actions import (DeclareLaunchArgument, ExecuteProcess,
                            IncludeLaunchDescription, RegisterEventHandler,
                            SetEnvironmentVariable)
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import (Command, EnvironmentVariable,
                                  FindExecutable, LaunchConfiguration,
                                  PathJoinSubstitution)
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

# ─────────────────────────────────────────────────────────────
#  Launch-time arguments
# ─────────────────────────────────────────────────────────────
ARGUMENTS = [
    # Gazebo world
    DeclareLaunchArgument('world_path', default_value=''),

    # Camera flags
    DeclareLaunchArgument('realsense_enabled', default_value='false',
                          description='Toggle Intel RealSense simulation'),
    DeclareLaunchArgument('realsense_mount',   default_value='top_plate_link',
                          description='Parent link the camera is welded to'),
    DeclareLaunchArgument('realsense_xyz',     default_value='0 0 0.50',
                          description='XYZ offset (m) relative to mount link'),
    DeclareLaunchArgument('realsense_rpy',     default_value='0 0 0',
                          description='RPY offset (rad) relative to mount link'),
]

# ─────────────────────────────────────────────────────────────
#  Helper
# ─────────────────────────────────────────────────────────────
def pkg_share(pkg: str) -> PathJoinSubstitution:
    return PathJoinSubstitution([FindPackageShare(pkg)])


# ─────────────────────────────────────────────────────────────
#  Launch description
# ─────────────────────────────────────────────────────────────
def generate_launch_description() -> LaunchDescription:

    # ── Environment ──────────────────────────────────────────
    set_model_path = SetEnvironmentVariable(
        name='GAZEBO_MODEL_PATH',
        value=[
            EnvironmentVariable('GAZEBO_MODEL_PATH', default_value=''),
            '/usr/share/gazebo-11/models:',
            pkg_share('husky_description'), '/..'   # meshes for sensor arch
        ])

    set_plugin_path = SetEnvironmentVariable(
        name='GAZEBO_PLUGIN_PATH',
        value=[
            EnvironmentVariable('GAZEBO_PLUGIN_PATH', default_value=''),
            ':',
            pkg_share('realsense_gazebo_plugin'), '/lib'
        ])

    # ── Xacro → URDF ────────────────────────────────────────
    husky_xacro   = pkg_share('husky_description') / 'urdf' / 'husky.urdf.xacro'
    ctrl_yaml     = pkg_share('husky_control')     / 'config' / 'control.yaml'

    robot_desc = {
        'robot_description': Command([
            FindExecutable(name='xacro'), ' ', husky_xacro,
            ' ', 'is_sim:=true',
            ' ', 'gazebo_controllers:=', ctrl_yaml,
            ' ', 'realsense_enabled:=',   LaunchConfiguration('realsense_enabled'),
            ' ', 'realsense_mount:=',     LaunchConfiguration('realsense_mount'),
            ' ', 'realsense_xyz:="',      LaunchConfiguration('realsense_xyz'), '"',
            ' ', 'realsense_rpy:="',      LaunchConfiguration('realsense_rpy'), '"',
            ' ', 'name:=husky',
            ' ', 'prefix:=''',
        ])
    }

    # ── Core nodes ───────────────────────────────────────────
    rsp = Node(package='robot_state_publisher',
               executable='robot_state_publisher',
               parameters=[{'use_sim_time': True}, robot_desc],
               output='screen')

    js_broadcaster = Node(package='controller_manager', executable='spawner',
                          arguments=['joint_state_broadcaster', '-c',
                                     '/controller_manager'],
                          output='screen')

    husky_vel = Node(package='controller_manager', executable='spawner',
                     arguments=['husky_velocity_controller', '-c',
                                '/controller_manager'],
                     output='screen')

    defer_vel = RegisterEventHandler(OnProcessExit(
        target_action=js_broadcaster, on_exit=[husky_vel]))

    # ── Gazebo server / client ──────────────────────────────
    gzserver = ExecuteProcess(
        cmd=['gzserver', '-s', 'libgazebo_ros_init.so',
             '-s', 'libgazebo_ros_factory.so',
             LaunchConfiguration('world_path')],
        output='screen')

    gzclient = ExecuteProcess(cmd=['gzclient'], output='screen')

    # ── Spawn Husky into Gazebo ─────────────────────────────
    spawn = Node(package='gazebo_ros', executable='spawn_entity.py',
                 name='spawn_husky',
                 arguments=['-entity', 'husky', '-topic', 'robot_description'],
                 output='screen')

    # ── Optional accessory launch files (unchanged) ────────
    ctrl_launch   = PythonLaunchDescriptionSource(
        pkg_share('husky_control') / 'launch' / 'control.launch.py')
    teleop_launch = PythonLaunchDescriptionSource(
        pkg_share('husky_control') / 'launch' / 'teleop_base.launch.py')

    # ── Assemble LD ─────────────────────────────────────────
    ld = LaunchDescription(ARGUMENTS)
    ld.add_action(set_model_path)
    ld.add_action(set_plugin_path)
    ld.add_action(rsp)
    ld.add_action(js_broadcaster)
    ld.add_action(defer_vel)
    ld.add_action(gzserver)
    ld.add_action(gzclient)
    ld.add_action(spawn)
    ld.add_action(IncludeLaunchDescription(ctrl_launch))
    ld.add_action(IncludeLaunchDescription(teleop_launch))

    return ld
