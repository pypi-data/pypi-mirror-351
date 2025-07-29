from setuptools import setup, find_packages

setup(
    name="codexl",
    version="0.1.2",
    description="A tool to manage multiple git repositories and working directories",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "click>=8.0.0",
        "gitpython>=3.1.0",
        "pyyaml>=6.0",
        "questionary>=1.10.0",
    ],
    entry_points={
        "console_scripts": [
            "codexl=codexl.cli:main",
        ],
    },
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
) 