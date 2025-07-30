from setuptools import setup, find_packages
import os

# Read the long description from README.md
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="mongo-archviz",
    version="1.0.0",
    author="Rishi Aluri",
    author_email="rishialuri@gmail.com",
    description="A MongoDB schema report generator for visualizing database architecture.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rishicarter/mongo-archviz",
    license="MIT",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "pymongo>=3.11",
    ],
    extras_require={
        "test": ["mongomock>=3.19"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        # "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
