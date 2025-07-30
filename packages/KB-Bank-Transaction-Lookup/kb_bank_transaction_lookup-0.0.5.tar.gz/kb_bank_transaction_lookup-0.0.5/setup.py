import setuptools
import os

with open("README.md", "r") as fh:
    long_description = fh.read()

def get_requires():
    thisdir = os.path.dirname(__file__)
    reqpath = os.path.join(thisdir, 'requirements.txt')
    return [line.rstrip('\n') for line in open(reqpath)]

setuptools.setup(
    name="KB_Bank_Transaction_Lookup", # Replace with your own username
    version="0.0.5",
    author="Starseller",
    author_email="yjkutl717@gmail.com",
    description="KB Kookmin Bank library for easy inquiry (Selenium not used)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://starseller.co.kr",
    packages=setuptools.find_packages(),
    install_requires=get_requires(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    include_package_data=True,
    #data_files=[
    #    ('output_dir',['KB_Bank_Transaction_Lookup/assets/*.png']),
    #]
)