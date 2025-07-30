from setuptools import setup, find_packages

setup(
    name="test_gaa_test",  # Уникальное имя (замените на своё)
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A simple Python package with calculator and greeting functions.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/my_package",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)