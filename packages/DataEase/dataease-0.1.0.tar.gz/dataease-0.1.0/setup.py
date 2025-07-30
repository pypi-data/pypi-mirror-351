from setuptools import setup, find_packages

setup(
    name="DataEase",
    version="0.1.0",
    author="Praveen Anand",
    author_email="apraveen1012@gmail.com",
    description="A lightweight package to ease DataFrame cleaning and MySQL integration tasks",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Praveen-A1012/DataEase",
    project_urls={
        "Bug Tracker": "https://github.com/Praveen-A1012/DataEase/issues",
        "Co-Author: Rahul Anand": "mailto:rahullalgudi2004@gmail.com",
        "Co-Author: Joel Ishika Reddy Kandukuri": "mailto:joelishika2003@gmail.com"
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        "pandas>=1.3.0",
        "sqlalchemy>=1.4.0",
        "pymysql>=1.0.0"
    ],
    include_package_data=True,
    license="MIT"
)
