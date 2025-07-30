from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="ompay-paymentgateway",
    version="0.0.5",
    author="ompay",
    author_email="support@ompay.com",
    description="A Python library for the ompay payment gateway.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(include=['compiled_ompay_paymentgateway', 'compiled_ompay_paymentgateway.*']),
    package_dir={'': 'ompay_paymentgateway'},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords=["ompay", "paymentgateway"],
    python_requires='>=3.6',
    install_requires=[
        "requests",
    ],
)
