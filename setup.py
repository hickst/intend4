from setuptools import setup, find_packages

setup(
    name='intend4',
    version='0.0.2',
    packages=find_packages(),
    # package_data={'intend4': []},
    # include_package_data=True,
    install_requires=[],
    entry_points={
        'console_scripts': [
            'add_intended4=intend4.add_intended4:main',
        ]
    },
)
