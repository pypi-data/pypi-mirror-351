from setuptools import setup, find_packages

setup(
    name="mkxcli",  # unique name not already taken
    version="0.1",
    author="Martin V",
    author_email="your_email@example.com",  # optional
    description="A simple and easy CLI tool.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/mkxcli",  # optional
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # or your license
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    entry_points={
        "console_scripts": [
            "mkx=mkxcli.__main__:main",  # You run the tool by typing `mkx`
        ],
    },
    include_package_data=True,
    install_requires=[],
)
