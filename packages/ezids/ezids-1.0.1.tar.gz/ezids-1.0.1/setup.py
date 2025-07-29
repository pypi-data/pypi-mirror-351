from setuptools import setup, find_packages
from pathlib import Path

this_dir = Path(__file__).parent
long_description = (this_dir / "README.md").read_text(encoding="utf-8")

setup(
    name="ezids",
    version="1.0.1",
    description="A simple host-based intrusion detection system with a PyQt GUI.",

    long_description=long_description,
    long_description_content_type="text/markdown",

    author="Nolan Coe",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "PyQt6"
    ],
    entry_points={
        "gui_scripts": [
            "ezids = ezids.main:main"
        ]
    },
)
