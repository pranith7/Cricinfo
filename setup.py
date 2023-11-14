from setuptools import setup
setup(
  name = 'cricinfo',
  packages = ['cricinfo'], 
  version = '1.2.5',
  description = 'A library for fetching live cricket scores from cricbuzz',
  author = 'Pranith Pashikanti',
  author_email = 'pashikantipranith7867@gmail.com',
  license = 'GPLv2',
  url = 'https://github.com/pranith7/cricinfo', 
  # download_url = 'https://github.com/codophobia/pycricbuzz/tarball/2.4', 
  keywords = ['cricket', 'cricbuzz'], 
  install_requires=[
          'requests',
          'beautifulsoup4'
      ],
  classifiers = [],
)
