import os
from glob import glob
from setuptools import setup, find_packages

package_name = "orbitpysdk"

setup(
    name=package_name,
    version='0.0.0',
    package_dir={'':'src'},
    packages=find_packages(where='src'),
    data_files=[
        (os.path.join("share", package_name, "resource", "images", "faces"), glob('resource/images/faces/*.png')),
        (os.path.join("share", package_name, "resource", "images", "lips"), glob('resource/images/lips/*.png')),
        (os.path.join("share", package_name, "resource", "videos"), glob('resource/videos/blinking.mp4')),
    ],
    install_requires=['setuptools', 'pyqt5', 'opencv-python', 'pydub', 'sounddevice'],
    zip_safe=True,
    maintainer='Kalebu',
    maintainer_email='calebndatimana@gmail.com',
    description='TODO: package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
)