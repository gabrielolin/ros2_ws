from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='blackjack',
            executable='talker',
            name='computer_vision',
            output='screen'
        ),
        Node(
            package='blackjack',
            executable='listener',
            name='motor_controlller',
            output='screen'
        )
    ])
