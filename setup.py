from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as fh:
    install_requires = fh.read().splitlines()

setup(
    name="pycopyql",
    version="0.3.0",
    author="Matthew Turland",
    author_email="me@matthewturland.com",
    description="Exports a subset of data from a relational database",
    keywords="database relational data export tool utility",
    url="https://github.com/elazar/pycopyql",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Database",
        "Topic :: Utilities",
    ],
    entry_points={
        'console_scripts': [
            'pycopyql=pycopyql.cli:main',
        ],
    },
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=install_requires,
    packages=find_packages(),
    python_requires=">=3.5",
)
