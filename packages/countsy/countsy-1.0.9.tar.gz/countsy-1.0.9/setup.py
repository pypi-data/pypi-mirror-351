from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="countsy",
    version="1.0.9",
    author="Furkan Tandogan",
    description="Count lines of Python code in directories",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(where="."),
    package_dir={"countsy": "src"},
    entry_points={
        "console_scripts": [
            "countsy=src.cli:main"
        ],
    },
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

