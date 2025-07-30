from setuptools import setup

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="elvet",
    version="1.0.2",
    description=(
        "A neural network-based differential equation and variational problem solver"
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/elvet/elvet",
    author="J. Y. Araz, J. C. Criado, M. Spannowsky",
    author_email=(
        "jack.araz@durham.ac.uk, criadoalamo@gmail.es, michael.spannowsky@durham.ac.uk"
    ),
    license="MIT",
    packages=[
        "elvet",
        "elvet.math",
        "elvet.math.diffops",
        "elvet.minimizer",
        "elvet.solver",
        "elvet.system",
        "elvet.utils",
    ],
    python_requires=">=3.6",
    classifiers=[
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Scientific/Engineering :: Physics",
    ],
)
