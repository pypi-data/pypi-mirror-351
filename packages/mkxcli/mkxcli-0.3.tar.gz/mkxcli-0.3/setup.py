from setuptools import setup, find_packages

# Read the README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mkxcli",
    version="0.3",  # Always bump this when re-uploading
    author="Your Name",
    description="A simple CLI to make files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'make=mkxcli.main:main',  # match your actual code structure
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
