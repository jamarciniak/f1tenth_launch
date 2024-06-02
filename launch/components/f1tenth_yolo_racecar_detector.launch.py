# Copyright 2024 The Autoware Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import ExecuteProcess
from launch.actions import GroupAction
from launch.actions import IncludeLaunchDescription
from launch.actions import OpaqueFunction
from launch.actions import TimerAction
from launch.conditions import IfCondition
from launch.substitutions import FindExecutable
from launch.substitutions import LaunchConfiguration
from launch.substitutions import PathJoinSubstitution
from launch.launch_description_sources import FrontendLaunchDescriptionSource
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node
from launch_ros.actions import PushRosNamespace
import yaml


def launch_setup(context, *args, **kwargs):
    pkg_prefix = FindPackageShare('f1tenth_launch')


    with open(LaunchConfiguration('yolo_racecar_detector_param_file').perform(context), 'r') as f:
        yolo_perception_params = yaml.safe_load(f)['/**']['ros__parameters']

        yolo_perception_params['onnx_model_path'] = PathJoinSubstitution(
            [pkg_prefix, 'config/yolo_perception',
            yolo_perception_params['onnx_model_path']]
        ).perform(context)

        yolo_perception_params['trt_engine_path'] = PathJoinSubstitution(
            [pkg_prefix, 'config/yolo_perception',
            yolo_perception_params['trt_engine_path']]
        ).perform(context)

    
    yolo_racecar_detector_node = Node(
        package='yolo_racecar_detector',
        executable='yolo_racecar_detector_node_exe',
        name='yolo_racecar_detector_node',
        parameters=[
            yolo_perception_params
        ],
        output='screen',
        remappings=[
            ('/in/image', '/sensing/camera/image_raw'),
            ('/out/image', '/yolo_racecar_detector/viz/image_with_bboxes'),
            ('/out/objects', '/yolo_racecar_detector/objects')],
        arguments=['--ros-args', '--log-level', 'info', '--enable-stdout-logs'],
    )


    return [
        yolo_racecar_detector_node
    ]


def generate_launch_description():
    declared_arguments = []

    def add_launch_arg(name: str, default_value: str = None):
        declared_arguments.append(
            DeclareLaunchArgument(name, default_value=default_value)
        )

    add_launch_arg('yolo_racecar_detector_param_file')

    return LaunchDescription([
        *declared_arguments,
        OpaqueFunction(function=launch_setup)
    ])
