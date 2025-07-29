from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="fseasypygame",
    version="0.2.0",
    author="madhat",
    author_email="madhat625@gmail.com",
    description="A simplified pygame wrapper for easier game development",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/madhat386/fseasypygame",
    packages=find_packages(),
    install_requires=["pygame>=2.5.1"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
