from setuptools import setup, find_packages

setup(
    name='Intend4',
    version='0.4.0',
    packages=find_packages(),
    # package_data={'intend4': []},
    # include_package_data=True,
    install_requires=[],
    entry_points={
        'console_scripts': [
            'intend4 = intend4.intend4_cli:main',
        ]
    },
)
