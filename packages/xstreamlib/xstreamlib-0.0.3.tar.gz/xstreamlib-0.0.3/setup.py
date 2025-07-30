import setuptools 
from pathlib import Path

long_description = Path("README.md").read_text(encoding="utf-8")

setuptools.setup(
    name="xstreamlib",
    author="KeimaSenpai",
    author_email="KeimaSenpai@proton.me",
    version="0.0.3",
    long_description=long_description,
    py_modules=[
        "requests",
    ],
    packages=setuptools.find_packages(exclude=[".vscode"]),
)