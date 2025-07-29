from setuptools import setup

setup(
    name="raze3d",  # nome do pacote (tem que bater com o token e com o que vai pro PyPI)
    version="0.1.1",
    description="Pacote 3D muito daora para usar em seus projetos Python.",
    long_description="raze3D\nPacote 3D muito daora para usar em seus projetos Python.",
    long_description_content_type="text/markdown",
    author="Davi Carozo Rocha Sobral",
    packages=["raze3d"],  # ou find_packages()
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # troca pela tua licença
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
