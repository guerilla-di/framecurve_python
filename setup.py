from setuptools import setup

def get_version():
    import os
    import sys
    curdir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, curdir)
    import framecurve
    version = framecurve.__version__

    return ".".join(map(str, version))


setup(
name = 'framecurve',
version=get_version(),

author='Guerilla-DI',
description='Library for working with framecurve files, a type of animation curve that represents a variable-speed timewarp',
url='https://github.com/guerilla-di/framecurve_python',
license='MIT',

long_description="""\
A framecurve is a type of animation curve that represents a variable-speed timewarp. That is, a timewarp where footage accelerates and slows down. It's called a frame curve because instead of operating with changing speed values it operates in absolute frame correlations - it gives you a table of relationships from the frame in your scene to a frame in your animation or video.

See http://framecurve.org/ for more information
""",

py_modules = ['framecurve'],

classifiers=[
        "Development Status :: 4 - Beta",
        #"Development Status :: 5 - Production/Stable",

        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",

        # Versions supported
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",

        # Python impl's supported
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy", # tested pypy/1.7
        # Might as well test the following at some point:
        #"Programming Language :: Python :: Implementation :: IronPython",
        #"Programming Language :: Python :: Implementation :: Jython",
        #"Programming Language :: Python :: Implementation :: Stackless",

        # Unhelpfully vague categories
        "Topic :: Multimedia :: Video",
        "Topic :: Multimedia :: Video :: Non-Linear Editor",

]
)
