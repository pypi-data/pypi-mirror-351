from setuptools import setup, find_packages

setup(
    name='grupo3',
    version='0.1.0',
    author='Grupo 3 TIWM MADS 2ºAno',
    author_email='grupo3@example.com',
    description='Projeto do Grupo 3 - Gestao de consumo',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/DanilsonGG/Grupo-3',
    packages=find_packages(include=['grupo3', 'grupo3.*']),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=['tabulate']
)
