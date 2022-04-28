"""Setup for geojson-pydantic."""

from setuptools import find_packages, setup

with open("README.md") as f:
    readme = f.read()

# Runtime requirements.
inst_reqs = ["pydantic"]

extra_reqs = {
    "test": ["pytest", "pytest-cov"],
    "dev": ["pre-commit"],
}

setup(
    name="geojson-pydantic",
    python_requires=">=3.7",
    description="""Pydantic data models for the GeoJSON spec""",
    long_description=readme,
    long_description_content_type="text/markdown",
    classifiers=[
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.7",
        "Topic :: Scientific/Engineering :: GIS",
    ],
    keywords="geojson pydantic",
    author="Drew Bollinger",
    author_email="drew@developmentseed.org",
    url="https://github.com/developmentseed/geojson-pydantic",
    license="MIT",
    packages=find_packages(exclude=["tests"]),
    install_requires=inst_reqs,
    extras_require=extra_reqs,
    package_data={"geojson_pydantic": ["*.typed"]},
)
