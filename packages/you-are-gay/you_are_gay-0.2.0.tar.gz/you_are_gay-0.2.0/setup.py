from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="you-are-gay",
    version="0.2.0",
    author="Claude User",
    author_email="user@example.com",
    description="A package that displays a name with 'IS GAY' in a fancy way in the terminal",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/username/you-are-gay",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "you-are-gay=fancy_text.main:main",
        ],
    },
) 
