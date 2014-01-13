import os

from setuptools import find_packages
from setuptools import setup

version = '1.0'
project = 'mba'

install_requires=['pyramid>=1.0.2', 'pyramid_jinja2', 'pyramid_debugtoolbar']

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

setup(name=project,
      version=version,
      description="AddOn for Kotti",
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "License :: Repoze Public License",
        ],
      keywords='kotti addon',
      author='czzsunset',
      author_email='czzsunset@gmail.com',
      url='http://pypi.python.org/pypi/',
      license='bsd',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      tests_require=[],
      entry_points={
        'fanstatic.libraries': [
            'mba = mba.fanstatic:library',
        ],

        'paste.app_factory':[
            'main = mba:main'
        ]
      },

      # entry_points="""\
      # [paste.app_factory]
      # main = mba:main
      # """,
      extras_require={},
      message_extractors={'mba': [
            ('**.py', 'lingua_python', None),
            ('**.zcml', 'lingua_xml', None),
            ('**.pt', 'lingua_xml', None),
            ]},
      )
