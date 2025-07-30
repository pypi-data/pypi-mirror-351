from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="codeatlas",
    version="0.1.0",
    author="Rahul Bedjavalge",
    author_email="rahulinberlinn@gmail.com",
    description="A Python library for visualizing and understanding codebases.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rahulbedjavalge/codeatlas",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "flask", "networkx", "click"
    ],
    entry_points={
        'console_scripts': [
            'codeatlas=codeatlas.cli:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
