from setuptools import setup

setup(
    name='shortscore',
    version='0.5dev',
    packages=['shortscore'],
    long_description=open('README.md').read(),
    entry_points={
        'console_scripts': [
            'shortscore=shortscore.cli:main',
        ],
    },
)
