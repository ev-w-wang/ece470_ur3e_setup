from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'ur3e_description'

def glob_recursive(directory):
    files = []
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            files.append(os.path.join(root, filename))
    return files

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*.urdf') + glob('urdf/*.xacro')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
        *[(os.path.join('share', package_name, os.path.relpath(os.path.dirname(f))), [f]) 
          for f in glob_recursive('meshes')],
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='evwang',
    maintainer_email='everettwang@outlook.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
        ],
    },
)
