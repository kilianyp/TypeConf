import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="typeconf",
    version="0.1",
    author="Kilian Pfeiffer",
    author_email="kilian.pfeiffer@rwth-aachen.de",
    description="A static configuration parser for python using templates",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kilsenp/TypeConf",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
