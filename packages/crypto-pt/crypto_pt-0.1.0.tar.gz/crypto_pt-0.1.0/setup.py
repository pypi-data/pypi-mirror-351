# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

# Lê o conteúdo do README.md para a long_description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='crypto-pt',  # O nome que será usado no pip install: pip install crypto-pt
    version='0.1.0',
    author='Lucas Cordeiro',
    author_email='sirbritolucas@gmail.com',
    description='Uma biblioteca Python para criptografia e descriptografia RSA em português.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/kikkask/crypto-pt',
    packages=find_packages(exclude=['tests*', 'examples*']), # Encontra automaticamente o pacote 'crypto_pt'
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Security :: Cryptography',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
    keywords='rsa, cryptography, encryption, decryption, crypto, pt, portugues',
    project_urls={
        'Bug Reports': 'https://github.com/kikkask/crypto-pt/issues',
        'Source': 'https://github.com/kikkask/crypto-pt/',
    },
)
