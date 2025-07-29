from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="jitsreport",
    version="0.1.0",
    author="Surajit Das",
    author_email="mr.surajitdas@gmail.com",
    description="A package for generating detailed data analysis reports.",
    long_description=long_description,  # Use the variable we already read
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "numpy",
        "plotly",
        "scipy",
        "openpyxl",
        "statsmodels",
        "matplotlib",
    ],
    python_requires=">=3.7",
)
