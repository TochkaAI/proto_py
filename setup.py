from setuptools import setup, find_packages


# with open("README.md", "r") as fh:
#     long_description = fh.read()

setup(
    name="proto_py",
    version="1.1.0",
    description="package with proto_py for PointOfView",
    url="https://github.com/TochkaAI/proto_py",
    packages=find_packages(),
    python_requires='>=3.6',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
