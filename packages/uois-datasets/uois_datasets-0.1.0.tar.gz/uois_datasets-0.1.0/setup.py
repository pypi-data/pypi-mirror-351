from setuptools import setup, find_packages

setup(
    name="uois_datasets",
    version="0.1.0",
    description="PyTorch DataLoader for UOIS datasets (OCID, OSD, RobotPushing, iTeachHumanPlay)",
    author="Jishnu Jaykumar Padalunkal",
    author_email="jishnu.p@utdallas.edu",
    url="https://github.com/jishnujayakumar/uois_datasets",
    packages=find_packages(),
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