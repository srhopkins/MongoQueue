import os

from setuptools import setup

def read(*paths):
    """Build a file path from *paths* and return the contents."""
    with open(os.path.join(*paths), 'r') as f:
        return f.read()

setup(
    name='mongoqueue',
    version='0.1.0',
    description='Simple queuing using MongoDB backend and a hybrid of Queue and pymongo syntax.',
    long_description=(read('README.rst') + '\n\n' +
                      read('HISTORY.rst') + '\n\n' +
                      read('AUTHORS.rst')),
    url='https://github.com/srhopkins/mongoqueue',
    license='MIT',
    author='Steven R. Hopkins',
    author_email='srhopkins@gmail.com',
    install_requires=['pymongo'],
    py_modules=['mongoqueue'],
    include_package_data=True,
    classifiers=[
        'Private :: Do Not Upload',
    ],
)
