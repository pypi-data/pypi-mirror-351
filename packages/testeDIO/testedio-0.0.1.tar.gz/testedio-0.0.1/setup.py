from setuptools import setup, find_packages

with open("README.md", "r") as f:
  page_description = f.read()

with open("requirements.txt") as f:
  requirements = f.read().splitlines()

setup(
    name="testeDIO",
    version="0.0.1",
    author="GabrielTropia",
    author_email="gabriel_tropia@hotmail.com",
    description="Teste modulo",
    long_desciption=page_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Gtropia/image-processing-package",
    packages=find_packages(),
    install_requirements=requirements,
    python_requires=">=3.8"
)
