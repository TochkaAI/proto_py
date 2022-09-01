from setuptools import setup, find_packages


# with open("README.md", "r") as fh:
#     long_description = fh.read()

setup(
    name='pproto-py',
    version='1.3.2',
    description='pproto_py is Python implementation of "Point Of View" communication protocol',
    url="https://github.com/TochkaAI/pproto_py",
    packages=find_packages(),
    python_requires='>=3.6',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
