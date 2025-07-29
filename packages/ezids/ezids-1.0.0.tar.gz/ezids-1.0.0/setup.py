from setuptools import setup, find_packages

setup(
    name="ezids",
    version="1.0.0",
    description="A simple host-based intrusion detection system with a PyQt GUI.",
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
