from setuptools import setup, find_packages
from pathlib import Path


this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="aerialflightgen",
    version="0.1.2",  
    packages=find_packages(),
    install_requires=[],
    author="Thirumurugan",
    description="Custom drone flight plan generator from geojson",
    long_description=long_description,
    long_description_content_type="text/markdown",  
    license="MIT",
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "aerialgen = aerialflightgen.cli:main"
        ]
    }
)
