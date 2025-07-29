from setuptools import setup, find_packages

setup(
    name="currency_rate_bcv",                # Nombre del paquete
    version="0.1.0",                   # Versión inicial
    author="Jarvis Gabriel Huice Padron",
    author_email="jarvis.realg@gmail.com",
    description="Librería para obtener la tasa oficial del Euro y Dólar publicada por el Banco Central de Venezuela (BCV).",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/tuusuario/mi_libreria ",  # Repo público
    packages=find_packages(),
    install_requires=[
        "requests>=2.32.3",
        "bs4>=0.0.2",
    ],          # Encuentra automáticamente los paquetes
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
