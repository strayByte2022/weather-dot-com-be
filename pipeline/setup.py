from setuptools import find_packages, setup

setup(
    name="pipeline",
    packages=find_packages(exclude=["logs", "storage"]),
    install_requires=[
        "dagster", "confluent-kafka", "python-dotenv", "dagit", "requests"
    ],
    extras_require={"dev": ["dagster-webserver", "pytest"]},
)
