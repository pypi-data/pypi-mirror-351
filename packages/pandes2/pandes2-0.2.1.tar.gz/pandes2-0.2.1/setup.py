from setuptools import setup, find_packages

setup(
    name='pandes2',
    version='0.2.1',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'pandes2': ['recursiveNonrecursive.txt', 'divideAndConquer.txt', 'Greedy.txt','DP.txt', 'Backtracking.txt', 'stringMatching.txt', 'all.txt'],
    },
    author='Micheal Scofield',
    description='A sample package that prints text file content',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
)
