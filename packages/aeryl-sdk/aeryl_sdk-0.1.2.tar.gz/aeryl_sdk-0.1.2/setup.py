from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="aeryl-sdk",
    version="0.1.2",
    author="Aeryl AI",
    author_email="info@aeryl.ai",
    description="Aeryl SDK for chaos testing and error detection",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aeryl-ai/aeryl_sdk",
    package_dir={"": "src"},  # Tell setuptools packages are under src/
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "polars>=0.20.0",
        "scikit-learn>=1.3.0",
        "torch>=2.0.0",
        "tqdm>=4.65.0",
        "sentence-transformers>=2.2.0",
        "xgboost>=1.7.0"
    ],
) 