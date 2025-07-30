from setuptools import setup, find_packages

with open("README.md", "r") as f: #Apenas abre o arquivo e associa.
    page_description = f.read() #De fato faz a leitura e armazena na var.

with open("requirements.txt") as f:
    requirements = f.read().splitlines() #Usando splitlines cada linha do .txt vira um valor numa lista

setup(
    name="image_processing-DIOFORK",
    version="0.0.1",
    author="BritoWB",
    author_email="britowb24@gmail.com",
    description="Processador de imagens",
    long_description=page_description,
    long_description_content_type="text/markdown",
    url='https://github.com/britowb/image-processing-package',
    install_requires=requirements,
    python_requires=' >=3.8',
)