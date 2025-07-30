from setuptools import setup, find_packages

setup(
    name = "Cyda",
    version = "1.5.0",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'cyda = Cyda.main:main',
        ],
    }
)