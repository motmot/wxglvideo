from setuptools import setup

from motmot_utils import get_svnversion_persistent
version_str = '0.3.dev%(svnversion)s'
version = get_svnversion_persistent('wxglvideo/version.py',version_str)

setup(name='wxglvideo',
      version=version,
      author='Andrew Straw',
      author_email='strawman@astraw.com',
      license='BSD',
      packages = ['wxglvideo'],
      install_requires = ['imops>=0.3.dev275'],
      )
