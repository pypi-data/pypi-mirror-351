import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="apache-airflow-providers-sktvane",
    version="1.2.11",
    author="aidp",
    author_email="aidp@sktai.io",
    description="Provider for Apache Airflow. Implements apache-airflow-providers-sktvane package by skt",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=["airflow", "sktvane"],
    license="MIT",
    url="https://github.com/sktaiflow/sktvane-airflow-providers",
    download_url="https://github.com/sktaiflow/sktvane-airflow-providers",
    packages=setuptools.find_namespace_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=[
        "requests",
        "hvac",
        "pendulum",
        "python-dateutil",
        "google-cloud-bigquery",
        "google-auth",
        "slack-sdk",
        "apache-airflow-providers-slack>=9.0.0",
    ],
)
