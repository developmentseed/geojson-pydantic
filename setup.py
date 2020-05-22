"""Setup for geojson-pydantic."""

from setuptools import find_packages, setup

with open("README.md") as f:
    readme = f.read()

# Runtime requirements.
inst_reqs = ["pydantic", "geojson"]

extra_reqs = {
    "test": ["pytest", "pytest-cov"],
    "dev": ["pytest", "pytest-cov", "pre-commit"],
}

setup(
    name="geojson-pydantic",
    version="0.1.0",
    python_requires=">=3.6",
    description=u"""Pydantic data models for the GeoJSON spec""",
    long_description=readme,
    long_description_content_type="text/markdown",
    classifiers=[
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.6",
        "Topic :: Scientific/Engineering :: GIS",
    ],
    keywords="geojson pydantic",
    author=u"Drew Bollinger",
    author_email="drew@developmentseed.org",
    url="https://github.com/developmentseed/geojson-pydantic",
    license="MIT",
    packages=find_packages(exclude=["ez_setup", "examples", "tests"]),
    include_package_data=True,
    install_requires=inst_reqs,
    extras_require=extra_reqs,
)