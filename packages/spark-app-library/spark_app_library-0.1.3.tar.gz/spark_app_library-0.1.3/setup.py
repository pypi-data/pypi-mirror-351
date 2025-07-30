from setuptools import setup, find_packages

setup(
    name="spark-app-library",
    version="0.1.3",
    description="A library to simplify creating Spark apps.",
    author="Navid Farhadi",
    author_email="navid.farhadi@snapp.cab",
    url="https://gitlab.snapp.ir/data-team/data-engineering/apache-spark/spark-app-library",
    packages=find_packages(),
    install_requires=[
    ],
    python_requires=">=3.7",
)