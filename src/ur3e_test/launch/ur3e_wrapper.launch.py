import os
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess
from moveit_configs_utils import MoveItConfigsBuilder
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():

    urdf_path = get_package_share_directory("ur3_moveit_config") + "/config/ur3e.urdf.xacro"

    moveit_config = (
            MoveItConfigsBuilder("ur3")
            .robot_description(file_path=urdf_path)
            ).to_moveit_configs()

    moveit_move_group = Node(
            package="moveit_ros_move_group",
            executable="move_group",
            #output="screen",
            parameters=[moveit_config.to_dict()],
            output="log"
            )

    test_node = Node(
            package="ur3e_test",
            executable="ur3e_wrapper",
            output="screen",
            parameters=[moveit_config.to_dict()]
            )

    rviz_config_file = os.path.join(
            get_package_share_directory("ur3e_test"),
            "launch",
            "rviz_config.rviz")
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        output="log",
        arguments=["-d", rviz_config_file],
        parameters=[
            moveit_config.robot_description,
            moveit_config.robot_description_semantic,
            moveit_config.robot_description_kinematics,
            moveit_config.planning_pipelines,
            moveit_config.joint_limits,
        ],
    )

    robot_state_publisher = Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            name="robot_state_publisher",
            # output="both",
            parameters=[moveit_config.robot_description],
            output="log",
            )

    static_tf = Node(
            package="tf2_ros",
            executable="static_transform_publisher",
            name="static_transform_publisher",
            output="log",
            arguments=["--frame-id", "world", "--child-frame-id", "base_link"]
            )

    ros2_controllers_path = os.path.join(
            get_package_share_directory("ur3_moveit_config"),
            "config",
            "ros2_controllers.yaml"
            )
    ros2_control_node = Node(
            package="controller_manager",
            executable="ros2_control_node",
            parameters=[ros2_controllers_path],
            remappings=[
                ("/controller_manager/robot_description", "/robot_description"),
                ],
            output="both",
            )

    load_controllers = []
    for controller in [
            "ur3_arm_controller",
            "joint_state_broadcaster",
            ]:
        load_controllers += [
                ExecuteProcess(
                    cmd=["ros2 run controller_manager spawner {}".format(controller)],
                    shell=True,
                    output="screen",
                    )
                ]

    return LaunchDescription (
            [
                rviz_node,
                test_node,
                static_tf,
                robot_state_publisher,
                ros2_control_node,
                moveit_move_group
            ]
            + load_controllers
            )

