from setuptools import setup, find_packages

setup(
    name="itechsmart-supreme",
    version="1.0.0",
    description="Autonomous IT Infrastructure Healing Platform",
    author="iTechSmart Inc.",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "click>=8.1.0",
        "rich>=13.6.0",
    ],
    entry_points={
        "console_scripts": [
            "itechsmart-supreme=itechsmart_supreme.cli.commands:cli",
        ],
    },
    python_requires=">=3.11",
)
