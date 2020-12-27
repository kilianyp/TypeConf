import setuptools
import versioneer

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="typeconf",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author="Kilian Pfeiffer",
    author_email="kilian.pfeiffer@rwth-aachen.de",
    description="A static configuration parser for python using templates",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kilsenp/TypeConf",
    packages=setuptools.find_packages(where="src"),
    install_requires=[
        'pydantic',
        'omegaconf'
    ],
    package_dir={'': 'src'},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
