from setuptools import setup
setup(
  name = 'cricinfo',
  packages = ['cricinfo'],
  version = '1.3.0',
  description = 'A Python interface for live cricket scores, commentary, and scorecards from Cricbuzz',
  long_description = open('README.md', encoding='utf-8').read(),
  long_description_content_type = 'text/markdown',
  author = 'Pranith Pashikanti',
  author_email = 'pashikantipranith7867@gmail.com',
  license = 'GPLv2',
  url = 'https://github.com/pranith7/cricinfo',
  keywords = ['cricket', 'cricbuzz', 'scorecard', 'commentary', 'live-score'],
  python_requires = '>=3.8',
  install_requires=[
          'requests',
          'beautifulsoup4'
      ],
  classifiers = [
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',
          'Programming Language :: Python :: 3.10',
          'Programming Language :: Python :: 3.11',
          'Programming Language :: Python :: 3.12',
          'Topic :: Internet :: WWW/HTTP',
          'Topic :: Software Development :: Libraries :: Python Modules',
      ],
)
