from setuptools import setup, find_packages

setup(
    name="rape3D",             # nome do seu pacote
    version="0.1.0",           # versão inicial
    packages=find_packages(),  # detecta os pacotes (pasta com __init__.py)
    py_modules=["rape"],       # se for só um módulo .py sem pasta
    author="Davi Carozo Rocha Sobral",
    description="Pacote 3D sinistro",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
