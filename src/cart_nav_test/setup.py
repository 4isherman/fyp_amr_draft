from setuptools import setup
from glob import glob
import os

package_name = 'cart_nav_test'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        # Required by ament
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),

        ('share/' + package_name, ['package.xml']),

        # Launch files
        (os.path.join('share', package_name, 'launch'),
            glob('launch/*')),

        # URDF files
        (os.path.join('share', package_name, 'urdf'),
            glob('urdf/*')),

        # RViz configs
        (os.path.join('share', package_name, 'rviz'),
            glob('rviz/*')),

        # Config files
        (os.path.join('share', package_name, 'config'),
            glob('config/*')),

        # World files
        (os.path.join('share', package_name, 'worlds'),
            glob('worlds/*')),

        # Models
        (os.path.join('share', package_name, 'models'),
            glob('models/*')),

        # Maps
        (os.path.join('share', package_name, 'maps'),
            glob('maps/*')),

    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='kong',
    maintainer_email='shiunsoon.kong@yahoo.com',
    description='Cart navigation test package',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            "cmd_vel_subscriber = cart_nav_test.cmd_vel_subscriber:main",
            "semantic_bridge = cart_nav_test.semantic_bridge:main",
            # "yolo_pointcloud_fusion = cart_nav_test.yolo_pointcloud_fusion:main",
            "gps_covariance_fix = cart_nav_test.gps_covariance_fix:main",
            "odom_covariance_fix = cart_nav_test.odom_covariance_fix:main",
            "imu_covariance_fix = cart_nav_test.imu_covariance_fix:main",
        ],
    },
)