from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="aeryl_sdk",
    version="0.1.0",
    author="Aeryl AI",
    author_email="info@aeryl.ai",
    description="Aeryl SDK for Chaos Classification",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aeryl-ai/aeryl_sdk",
    package_dir={"": "src"},  # Tell setuptools packages are under src/
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.26.0",
        "polars>=0.20.0",
        "scikit-learn>=1.4.0",
        "torch>=2.2.0",
        "tqdm>=4.66.0",
        "sentence-transformers>=2.5.0",
        "xgboost>=2.0.0",
    ],
) 