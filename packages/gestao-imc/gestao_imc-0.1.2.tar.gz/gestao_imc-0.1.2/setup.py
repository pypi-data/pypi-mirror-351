from setuptools import setup, find_packages
from os import path

working_directory = path.abspath(path.dirname(__file__))

with open(path.join(working_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='gestao_imc',
    version='0.1.2',
    url='https://github.com/Goncalo-Soares12/MADS-Grupo-4---Gestao-IMC-',
    author='Gonçalo Soares, Ruben Abreu, Flávio Santos, Jessica Gonçalves',
    author_email='seu@email.com',
    description='Ferramenta para gestão de IMC com base em dados de pessoas.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=['pandas', 'matplotlib', 'datetime'],
)