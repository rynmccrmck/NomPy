from setuptools import setup, find_packages

setup(
    name='nompy',
    version='0.0.1',
    author='Ryan McCormack',
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    url='http://pypi.python.org/pypi/NomPy/',
    license='LICENSE.txt',
    description='An awesome package for guessing gender from names.',
    long_description=open('README.md').read(),
    install_requires=[
        "protobuf",
    ],
)
