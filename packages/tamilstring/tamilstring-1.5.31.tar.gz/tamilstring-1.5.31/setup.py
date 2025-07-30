from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="tamilstring",
    version="1.5.31",
    author="boopalan",
    author_email="contact.boopalan@gmail.com",
    description="tamilstring helps to handle tamil unicode characters lot more easier",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/boopalan-dev/tamilstring",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[],
    extras_require={
        "dev": [
            "pytest>=6.0",
        ],
    },
)