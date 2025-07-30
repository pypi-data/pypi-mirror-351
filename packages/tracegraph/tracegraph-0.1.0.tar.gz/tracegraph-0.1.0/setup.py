from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="tracegraph",
    version="0.1.0",
    author="Abdul Rafey",
    author_email="abdulrafey38@gmail.com",
    description="A Python library for tracing and visualizing function calls",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/abdulrafey38/tracegraph",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Debuggers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "graphviz>=0.20.1",
    ],
    entry_points={
        "console_scripts": [
            "tracegraph=tracegraph.cli:main",
        ],
    },
) 