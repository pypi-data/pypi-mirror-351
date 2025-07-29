from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as readme_file:
    long_description = readme_file.read()

setup(
    name="DjangoSharepointStorage",
    version="1.1.7",
    author="Melih Sünbül",
    author_email="m.sunbul@lund-it.com",
    description="A Python library to use SharePoint as storage backend for your Django application",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/LundIT/DjangoSharepointStorage",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "django",
        "Office365-REST-Python-Client",
    ],
    python_requires='>=3.6',
)
