from setuptools import setup, find_packages

setup(
    name='mkxcli',
    version='0.2',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'make=mkxcli.main:main',  # 'make' command runs main() in mkxcli/main.py
        ],
    },
    author='Your Name',
    description='Simple CLI tool called make',
    python_requires='>=3.6',
)
