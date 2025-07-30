from setuptools import setup, find_packages

setup(
    name="python-nameof",
    version="1.0.0",
    description="A Python implementation of the C# nameof operator.",
    author="Alessio Lombardi",
    author_email="work@alelom.com",
    packages=find_packages(),
    py_modules=["nameof"],
    package_dir={"": "."},
    url="https://github.com/yourusername/python-nameof",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
