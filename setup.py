from setuptools import setup, find_packages

setup(
    name='intend4',
    version='2.2.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'intend4 = intend4.intend4_cli:main',
        ]
    },
)
