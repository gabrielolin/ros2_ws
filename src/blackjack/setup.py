from setuptools import find_packages, setup

package_name = 'blackjack'
submodules = "blackjack/model"

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/blackjack_launch.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='mustache',
    maintainer_email='gabrielolin@g.ucla.edu',
    description='Blackjack Game',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
		'talker = blackjack.app_multithread:main',
		'listener = blackjack.motor_control:main',
        ],
    },
)
