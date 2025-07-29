from setuptools import setup, find_packages

setup(
    name="aerialflightgen",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[],
    author="Thirumurugan",
    description="Custom drone flight plan generator from geojson",
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
