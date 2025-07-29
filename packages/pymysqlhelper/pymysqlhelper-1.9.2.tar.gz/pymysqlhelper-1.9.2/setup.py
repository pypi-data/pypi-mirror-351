from setuptools import setup, find_packages

with open("README.md", 'r') as f:
    description = f.read()

setup(
    name="pymysqlhelper",
    version="1.9.2",
    description="A simple MySQL database helper for easy interactions",
    author="DEAMJAVA",
    author_email="deamminecraft3@gmail.com",
    packages=find_packages(),
    install_requires=["pymysql", "sqlalchemy"],
    python_requires=">=3.6",
    entry_points={"console_scripts":["pymysqlhelper = pymysqlhelper:pymysqlhelper_check",
                                     "pymysqlhelper-license = pymysqlhelper:pymysqlhelper_license"]},
    long_description=description,
    long_description_content_type='text/markdown'
)
