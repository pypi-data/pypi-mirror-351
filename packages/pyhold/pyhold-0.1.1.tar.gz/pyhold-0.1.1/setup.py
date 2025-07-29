from setuptools import setup, find_packages

setup(
    name='pyhold',
    version='0.1.1',
    packages=find_packages(include=['pyhold', 'pyhold.*']),
    install_requires=[],
    author='Anjan Bellamkonda',
    description='A lightweight, persistent, dictionary-style key-value store with GUI support',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/AnjanB3012/pyhold',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)