from setuptools import setup, find_packages
import os

kws = {}

setup(name='motmot.wxglvideo',
      description='wx/OpenGL viewer of image sequences',
      long_description = \
"""Allows for rapid display and resizing/rotation of images by
offloading the image operations to OpenGL.

This is a subpackage of the motmot family of digital image utilities.
""",
      version='0.6.7',
      author='Andrew Straw',
      author_email='strawman@astraw.com',
      url='http://code.astraw.com/projects/motmot',
      license='BSD',
      zip_safe=True,
      packages = find_packages(),
      namespace_packages = ['motmot'],
      package_data = {'motmot.wxglvideo':['demo.xrc']},
      entry_points = {'gui_scripts': ['wxglvideo_demo=motmot.wxglvideo.demo:main',
                                      'wxglvideo_demo_overlay=motmot.wxglvideo.demo_overlay:main',
                                      ]},
      **kws)
