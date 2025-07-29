from setuptools import setup, find_packages

setup(
    name="raze3d",
    version="0.1.0",
    packages=find_packages(),  # só se tiver pasta com __init__.py
    # py_modules=["rape"],    # remove se usar find_packages()
    author="Davi Carozo Rocha Sobral",
    description="Pacote 3D sinistro",
    long_description=open("README.md", encoding='utf-8').read(),
    long_description_content_type="text/markdown",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
