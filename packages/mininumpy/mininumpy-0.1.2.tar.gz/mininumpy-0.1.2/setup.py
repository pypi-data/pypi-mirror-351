from setuptools import setup, find_packages

setup(
    name="mininumpy",
    version="0.1.0",
    author="Fahad Haroon",
    author_email="fahadharoon678@gmail.com",
    description="A simplified numpy-like library with parallel computing support",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/fahad-678/mininumpy",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    keywords="numpy array parallel computing educational",
)