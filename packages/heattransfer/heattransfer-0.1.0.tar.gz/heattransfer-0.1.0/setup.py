from setuptools import setup, find_packages

setup(
    name="heattransfer",
    version="0.1.0",
    author="Thiago",
    author_email="thiagolablonsk@gmail.com",
    description="Um pacote para cálculo de transferência de calor entre dois tubos concêntricos.",
    long_description = open("README.md", encoding="utf-8").read(),

    long_description_content_type="text/markdown",
    url="https://github.com/ThiagoLabM",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
