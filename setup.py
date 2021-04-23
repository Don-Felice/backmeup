from setuptools import setup


setup(
    name='backmeup',
    version='0.1.0',
    author='Felix Segerer',
    packages=['backmeup', 'tests'],
    license='LICENSE',
    description='Simple tool for backup tasks',
    entry_points={
         'console_scripts': [
             'backmeup = backmeup.__main__:main',
         ],
     }
)
