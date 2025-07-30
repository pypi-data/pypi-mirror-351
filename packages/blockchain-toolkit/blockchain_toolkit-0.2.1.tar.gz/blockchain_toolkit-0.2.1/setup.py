from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="blockchain_toolkit",
    version="0.2.1",
    author="AltF4444",
    description="Универсальная библиотека для взаимодействия с Ethereum-блокчейном с поддержкой AES-шифрования.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AltplusF4444/chain_tool",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=[
        'web3>=5.31.1',
        'cryptography>=36.0.1'
    ]
)