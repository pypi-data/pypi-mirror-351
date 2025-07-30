from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="rpa-driver-downloader",
    version="0.2.0",
    author="Ruan Chaves Machado",
    author_email="whiterun092@gmail.com",
    description="A Python package to automatically download and manage WebDrivers for Gecko, Chrome, and Edge.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ruanSTT/rpa-driver-downloader",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "Topic :: Utilities",
    ],
    python_requires='>=3.7, <=3.12.3',
    install_requires=[
        "requests>=2.31.0"
    ],
    include_package_data=True,
)
