# ----------------------------------------------------------------------------------------------------
# Work done while being at the Intelligent Robotics and Vision Lab at the University of Texas, Dallas
# Please check the licenses of the respective works utilized here before using this script.
# 🖋️ Jishnu Jaykumar Padalunkal (2025).
# ----------------------------------------------------------------------------------------------------

from setuptools import setup, find_packages

setup(
    name="uois_toolkit",
    version="0.1.0",
    package_dir={"uois_toolkit.core": "core"},
    description="A toolkit for UOIS task",
    author="Jishnu Jaykumar Padalunkal",
    author_email="jishnu.p@utdallas.edu",
    url="https://github.com/jishnujayakumar/uois_datasets",
    install_requires=[
        "torch>=1.9.0",
        "torchvision>=0.10.0",
        "opencv-python>=4.5.0",
        "numpy>=1.19.0",
        "scipy>=1.5.0",
        "pycocotools>=2.0.2",
        "detectron2>=0.6",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
