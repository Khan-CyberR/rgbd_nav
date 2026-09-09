import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'pointcloud_to_occupancy'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), ['launch/occupancy_with_rviz.launch.py']),
        (os.path.join('share', package_name, 'launch'), ['launch/navigation.launch.py']),
        (os.path.join('share', package_name, 'config'), ['config/point.rviz']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='kcc',
    maintainer_email='12213034@mail.sustech.edu.cn',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
    'console_scripts': [
        'pointcloud_to_occupancy = pointcloud_to_occupancy.pointcloud_to_occupancy_node:main',
    ],
},
)
