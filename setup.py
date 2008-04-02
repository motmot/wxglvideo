from setuptools import setup, find_packages
import os

kws = {}
if not int(os.getenv( 'DISABLE_INSTALL_REQUIRES','0' )):
    kws['install_requires'] = ['numpy>=1.0.4',
                          'motmot.imops>=0.5.2.dev',
                          'pyglet>=1.0',
                          'wxPython>=2.8',
                          'pygarrayimage>=0.0.2',
                          ],

setup(name='motmot.wxglvideo',
      description='wx/OpenGL viewer of image sequences',
      long_description = \
"""Allows for rapid display and resizing/rotation of images by
offloading the image operations to OpenGL.

This is a subpackage of the motmot family of digital image utilities.
""",
      version='0.6.1',
      author='Andrew Straw',
      author_email='strawman@astraw.com',
      url='http://code.astraw.com/projects/motmot',
      license='BSD',
      zip_safe=True,
      packages = find_packages(),
      namespace_packages = ['motmot'],
      package_data = {'motmot.wxglvideo':['demo.xrc']},
      entry_points = {'gui_scripts': ['wxglvideo_demo=motmot.wxglvideo.demo:main',
                                      ]},
      **kws)
