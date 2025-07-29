# setup.py
from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="photonkit",  # 🔄 changed from 'photonic'
    version="0.2.1",
    description="PhotonKit -- A mildly opinionated toolkit for managing your camera photo collection",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Rahul Singh",
    license="MIT",
    packages=find_packages(include=["backup", "backup.*"]),
    entry_points={
        "console_scripts": [
            "photonkit = backup.photo_backup:main"  # 👈 CLI command will now be `photonkit`
        ]
    },
    install_requires=[],
    python_requires=">=3.8",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS :: MacOS X",
        "Programming Language :: Python :: 3",
        "Environment :: Console",
        "Topic :: Utilities",
    ],
)
