from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="flet_table",
    version="2.0.0",
    author="Luchiano Farrely",
    author_email="dreevxqcrypto@gmail.com",
    description="This library provides normal table elements by just using flet framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tzinchy/flet_table",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        "anyio==4.9.0",
        "bcrypt==4.3.0",
        "certifi==2025.1.31",
        "et_xmlfile==2.0.0",
        "flet==0.27.6",
        "flet-desktop==0.27.6",
        "h11==0.14.0",
        "httpcore==1.0.8",
        "httpx==0.28.1",
        "idna==3.10",
        "iniconfig==2.1.0",
        "numpy==2.2.4",
        "oauthlib==3.2.2",
        "openpyxl==3.1.5",
        "packaging==24.2",
        "pandas==2.2.3",
        "pluggy==1.5.0",
        "PyMySQL==1.1.1",
        "pytest==8.3.5",
        "python-dateutil==2.9.0.post0",
        "pytz==2025.2",
        "repath==0.9.0",
        "simpledatatable==0.3.4",
        "six==1.17.0",
        "sniffio==1.3.1",
        "SQLAlchemy==2.0.40",
        "typing_extensions==4.13.2",
        "tzdata==2025.2"
    ],
)