from setuptools import setup, find_packages

setup(name='motmot.wxglvideo',
      description='wx/OpenGL viewer of image sequences (part of the motmot camera packages)',
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
                                      ]}
      )
