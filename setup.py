from setuptools import setup, find_packages
setup(
name = 'checkTvEps',
version='0.1',

author='dbr/Ben',
description='A collection of utilties to verify TV episodes match a naming scheme',
url='http://github.com/dbr/checktveps/tree/master',
license='GPLv2',

py_modules = ['filename_config', 'checkTvEps', 'checkFilms', 'autoPathTv'],
entry_points = {
    'console_scripts':[
        'checkTvEps = checkTvEps:main',
        'checkFilms = checkFilms:main',
        'autoPathTv = autoPathTv:main'
    ]
},

classifiers=[
    "Environment :: Console",
    "Intended Audience :: End Users/Desktop",
    "License :: OSI Approved :: GNU General Public License (GPL)",
    "Natural Language :: English",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Topic :: Multimedia",
    "Topic :: Utilities"
]
)