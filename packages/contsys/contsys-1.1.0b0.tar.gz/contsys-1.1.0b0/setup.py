from setuptools import setup, find_packages
import pathlib

here= pathlib.Path(__file__).parent.resolve()
long_description= (here / "README.md").read_text(encoding="utf-8")

setup(
    name="contsys",
    version="1.1.0-beta",
    description="Python library simplifying system script management with handy functions like clearing the console, setting the window title, and detecting the operating system (Windows, Linux, macOS).",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="G-Azon",
    author_email="G-Azon782345@protonmail.com",
    license="MIT",
    packages=find_packages(),
    install_requires=['psutil'],  
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.11',
)
