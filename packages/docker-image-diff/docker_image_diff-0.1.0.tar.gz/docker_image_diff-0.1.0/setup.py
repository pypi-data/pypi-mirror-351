from setuptools import setup, find_packages

# Read the README for the long description
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="docker-image-diff",
    version="0.1.0",
    author="Junghyun Kwon",
    author_email="",
    description="Generate and apply diffs between Docker image tar archives",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/junghyun3/docker-image-diff", 
    packages=find_packages(), 
    py_modules=["dockerdiff"] if not find_packages() else [],  # fallback if single module
    python_requires=">=3.10",
    entry_points={
        "console_scripts": [
            "dockerdiff=dockerdiff.main:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    license="Apache-2.0",
)
