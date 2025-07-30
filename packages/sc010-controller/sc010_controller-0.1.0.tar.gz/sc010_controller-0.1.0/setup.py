from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="sc010-controller",
    version="0.1.0",
    author="Justin Faulk",
    author_email="jfaulk@proitav.us",  # Update this
    description="A Python library for controlling SC010 AV over IP controllers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/sc010-controller",  # Update this
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Multimedia :: Video",
    ],
    python_requires=">=3.7",
    install_requires=[
        "telnetlib3>=2.0.0",
    ],
)
