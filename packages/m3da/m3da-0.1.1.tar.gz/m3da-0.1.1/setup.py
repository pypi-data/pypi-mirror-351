from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="m3da",
    version="0.1.1",
    author="Mutiibwa Grace Peter",
    author_email="androm3dalabs@gmail.com",
    description="A lightweight package for image classification using ONNX models",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/GracePeterMutiibwa/m3da",
    project_urls={
        "Bug Tracker": "https://github.com/GracePeterMutiibwa/m3da/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        "numpy>=1.19.0",
        "onnxruntime>=1.7.0",
        "Pillow>=8.0.0",
    ],
    keywords="onnx, machine learning, deep learning, image classification, ai",
)
