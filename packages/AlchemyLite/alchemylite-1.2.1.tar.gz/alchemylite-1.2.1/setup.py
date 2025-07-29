from setuptools import setup, find_packages

def readme():
  with open('README.md', 'r') as f:
    return f.read()

setup(
  name='AlchemyLite',
  version='1.2.1',
  author='Yuri Voskanyan',
  author_email='yura.voskanyan.2003@mail.ru',
  description='A library that simplifies CRUD operations with database.',
  long_description=readme(),
  long_description_content_type='text/markdown',
  url='https://github.com/Garinelli/AlchemyLite',
  packages=find_packages(),
  install_requires=['asyncpg>=0.30.0', 'psycopg-pool>=3.2.3',
                    'SQLAlchemy>=2.0.36', 'psycopg>=3.2.3', 'psycopg2-binary>=2.9.10', 'psycopg-binary==3.2.4', 'aiosqlite==0.21.0',
                    ],
  classifiers=[
    'Programming Language :: Python :: 3.10',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent'
  ],
  keywords=['AlchemyLite, alchemylite, Alchemy lite, alchemy lite', 'crud sqlalchemy', 'python crud'],
  project_urls={
    'Documentation': 'https://github.com/Garinelli/AlchemyLite'
  },
  python_requires='>=3.10'
)