from setuptools import setup, find_packages

setup(name='motmot.wxglvideo',
      description='wx/OpenGL viewer of image sequences (part of the motmot camera packages)',
      version='0.6.1',
      author='Andrew Straw',
      author_email='strawman@astraw.com',
      install_requires = ['numpy>=1.0.4',
                          'motmot.imops>=0.5.2.dev',
                          #'pyglet>=1.0', # pyglet egg is broken
                          'wxPython>=2.8',
                          'pygarrayimage>=0.0.2',
                          ],
      url='http://code.astraw.com/projects/motmot',
      license='BSD',
      zip_safe=True,
      packages = find_packages(),
      namespace_packages = ['motmot'],
      package_data = {'motmot.wxglvideo':['demo.xrc']},
      entry_points = {'gui_scripts': ['wxglvideo_demo=motmot.wxglvideo.demo:main',
                                      ]}
      )
