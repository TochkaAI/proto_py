from setuptools import setup, find_packages


# with open("README.md", "r") as fh:
#     long_description = fh.read()

setup(
    name="pyproto",
    version="0.0.4",
    description="package with pyproto for PointOfView",
    url="https://github.com/TochkaAI/pyproto",
    packages=find_packages(),
    python_requires='>=3.6',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
